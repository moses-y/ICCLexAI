"""Measure the transcription gate on the set built by build.py.

1. Transcribes every item with the production call (icclex.agents.llm.transcribe): once auto-detected and
   once forced to each language in config.SPEECH_LANGUAGES. Raw replies are cached per model under
   var/eval/transcription/cache/, so a rerun only calls the model for what is missing.
2. Replays the cache through the production gate (icclex.agents.audio_video._trusted_transcript) for a grid
   of confidence floors and reports, per floor pair:
     speech good   kept, and word error rate <= GOOD_WER against the FLEURS reference
     speech bad    kept, but WER above GOOD_WER: a wrong-language or invented transcript reached review
     no-speech     any transcript kept from a clip with no speech: invented outright

    python evals/transcription/run.py            # call what is missing, then report
    python evals/transcription/run.py --offline  # report from the cache only
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "backend"))

from icclex import config  # noqa: E402
from icclex.agents import audio_video, llm  # noqa: E402
from icclex.agents.base import AgentTransient  # noqa: E402

ROOT = Path(__file__).resolve().parents[2] / "var" / "eval" / "transcription"
GOOD_WER = 0.5
AUTO_FLOORS = (-1.0, -0.8, -0.6, -0.5, -0.4)
FORCED_FLOORS = (-0.6, -0.5, -0.4, -0.3)


def _cache_path(item_id: str, language: str | None) -> Path:
    return ROOT / "cache" / config.TRANSCRIBE_MODEL.replace("/", "_") / f"{item_id}.{language or 'auto'}.json"


def _fill_cache(items: list[dict]) -> int:
    calls = 0
    for i, it in enumerate(items, 1):
        for language in (None, *config.SPEECH_LANGUAGES):
            path = _cache_path(it["id"], language)
            if path.exists():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                result, _ = llm.transcribe(ROOT / "audio" / f"{it['id']}.wav", f"{it['id']}.wav", language=language)
            except AgentTransient as exc:
                print(f"stopped at item {i}/{len(items)} after {calls} calls: {exc}\nrerun later to continue")
                return calls
            path.write_text(json.dumps(result, ensure_ascii=False))
            calls += 1
        if i % 20 == 0:
            print(f"  {i}/{len(items)} items, {calls} calls this run", flush=True)
    return calls


def _cached_transcribe(path, filename, language=None):
    cached = _cache_path(Path(path).stem, language)
    if not cached.exists():
        raise LookupError(f"not cached: {cached.name}; run without --offline")
    return json.loads(cached.read_text()), config.TRANSCRIBE_MODEL


def _words(text: str | None) -> list[str]:
    text = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"[^\w\s']", " ", text).split()


def wer(reference: str, hypothesis: str) -> float:
    ref, hyp = _words(reference), _words(hypothesis)
    row = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, row[0] = row[0], i
        for j, h in enumerate(hyp, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (r != h))
    return row[-1] / max(len(ref), 1)


def _evaluate(items: list[dict]) -> list[dict]:
    rows = []
    for it in items:
        result, _, tried = audio_video._trusted_transcript(ROOT / "audio" / f"{it['id']}.wav")
        text = (result or {}).get("text") or ""
        kept = result is not None and any(ch.isalpha() for ch in text)  # the agent's own "no speech" rule
        rows.append({**it, "kept": kept, "text": text, "tried": tried,
                     "wer": wer(it["reference"], text) if kept and it["kind"] == "speech" else None})
    return rows


def _summary(rows: list[dict]) -> dict:
    speech = [r for r in rows if r["kind"] == "speech"]
    none = [r for r in rows if r["kind"] == "no_speech"]
    good = sum(r["kept"] and r["wer"] <= GOOD_WER for r in speech)
    bad = sum(r["kept"] and r["wer"] > GOOD_WER for r in speech)
    return {"good": good / len(speech), "bad": bad / len(speech), "invented": sum(r["kept"] for r in none) / len(none)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="use the cache only; never call the model")
    args = ap.parse_args()

    manifest = ROOT / "manifest.jsonl"
    items = [json.loads(line) for line in manifest.read_text().splitlines()] if manifest.exists() else []
    if not items or not any(it["kind"] == "speech" for it in items) or not any(it["kind"] == "no_speech" for it in items):
        raise SystemExit(f"nothing to measure: build the set first (python evals/transcription/build.py); {manifest}")
    if not args.offline:
        if not (config.GROQ_API_KEY and config.TRANSCRIBE_MODEL):
            raise SystemExit("GROQ_API_KEY or ICCLEX_TRANSCRIBE_MODEL is not set")
        print(f"{config.TRANSCRIBE_MODEL}: {_fill_cache(items)} new calls")
    missing = [it["id"] for it in items for lang in (None, *config.SPEECH_LANGUAGES) if not _cache_path(it["id"], lang).exists()]
    if missing:
        raise SystemExit(f"{len(missing)} transcriptions not cached yet (e.g. {missing[0]}); rerun without --offline")

    audio_video.transcribe = _cached_transcribe  # replay the cache through the production gate
    current = (config.TRANSCRIBE_MIN_LOGPROB, config.TRANSCRIBE_FORCED_MIN_LOGPROB)

    print(f"\n{len(items)} items, model {config.TRANSCRIBE_MODEL}, languages {list(config.SPEECH_LANGUAGES)}")
    print(f"good = kept with WER <= {GOOD_WER}; bad = kept with higher WER; invented = kept from a no-speech clip\n")
    print(f"{'auto floor':>10} {'forced floor':>12} {'speech good':>12} {'speech bad':>11} {'no-speech invented':>19}")
    for auto in AUTO_FLOORS:
        for forced in FORCED_FLOORS:
            config.TRANSCRIBE_MIN_LOGPROB, config.TRANSCRIBE_FORCED_MIN_LOGPROB = auto, forced
            s = _summary(_evaluate(items))
            mark = "  <- current" if (auto, forced) == current else ""
            print(f"{auto:>10} {forced:>12} {s['good']:>12.0%} {s['bad']:>11.0%} {s['invented']:>19.0%}{mark}")

    config.TRANSCRIBE_MIN_LOGPROB, config.TRANSCRIBE_FORCED_MIN_LOGPROB = current
    rows = _evaluate(items)
    groups = defaultdict(list)
    for r in rows:
        groups[(r["kind"], r["language"] or "-", r["condition"])].append(r)
    print(f"\nAt the current floors {current}:")
    print(f"{'kind':<10} {'lang':<5} {'condition':<9} {'n':>3} {'kept':>5} {'good':>5} {'median WER kept':>16}")
    for (kind, lang, cond), rs in sorted(groups.items()):
        kept = [r for r in rs if r["kept"]]
        good = sum(r["wer"] is not None and r["wer"] <= GOOD_WER for r in kept)
        med = f"{statistics.median(r['wer'] for r in kept):.2f}" if kept and kind == "speech" else "-"
        print(f"{kind:<10} {lang:<5} {cond:<9} {len(rs):>3} {len(kept):>5} {good:>5} {med:>16}")
    report = ROOT / "last_report.jsonl"
    with open(report, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nper-item results at the current floors: {report}")


if __name__ == "__main__":
    main()
