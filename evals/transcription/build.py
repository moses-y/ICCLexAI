"""Build the transcription evaluation set from FLEURS (google/fleurs on Hugging Face), dev split.

Why: on 2026-11-06 Whisper turned two Nairobi street clips into Spanish and Malay phrases, and noisy
Swahili into Greek letters. The confidence floors that now withhold such transcripts were set from 7 clips;
this set lets them be measured on hundreds.

Items, all 16 kHz mono WAV under var/eval/transcription/ (git-ignored):
  speech: one clip per distinct FLEURS sentence, per language, in three conditions:
          clean, pink noise at SNR 5 dB, and crowd babble (6 other speakers) at SNR 5 dB
  no_speech: pink noise, brown noise, and 6-speaker babble alone. Any transcript of these is invented.

FLEURS is read speech recorded in quiet rooms; the noise conditions approximate field footage, they do not
replace it. There is no Sheng in FLEURS.

    python evals/transcription/build.py --per-language 25
"""

import argparse
import csv
import io
import json
import subprocess
import tarfile
import urllib.request
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "var" / "eval" / "transcription"
FLEURS = "https://huggingface.co/datasets/google/fleurs/resolve/main/data/{lang}/{path}"
# FLEURS config -> the language code ICCLexAI's SPEECH_LANGUAGES uses.
LANGUAGES = {"sw_ke": "sw", "en_us": "en"}
RATE = 16000
SNR_DB = 5
BABBLE_SPEAKERS = 6
SEED = 20261106


# The dev split, the smallest (136 MB Swahili, 171 MB English); only its first ~10 MB is read, see _first_wavs.
SPLIT = "dev"


def _tsv(lang: str) -> list[dict]:
    with urllib.request.urlopen(FLEURS.format(lang=lang, path=f"{SPLIT}.tsv")) as r:
        rows = csv.reader(io.TextIOWrapper(r, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)
        return [{"sentence_id": row[0], "file": row[1], "text": row[2], "normalized": row[3],
                 "seconds": int(row[5]) / RATE} for row in rows]


def _first_wavs(lang: str, rows: dict[str, dict], n: int) -> list[tuple[dict, np.ndarray]]:
    """The first n clips in archive order that are 4-15 s long and from a sentence not already taken.
    Stopping there reads about 10 MB of the archive; sampling across it read nearly all of it."""
    out, sentences = [], set()
    with urllib.request.urlopen(FLEURS.format(lang=lang, path=f"audio/{SPLIT}.tar.gz")) as r:
        with tarfile.open(fileobj=r, mode="r|gz") as tar:
            for member in tar:
                row = rows.get(Path(member.name).name)
                if row is None or not 4 <= row["seconds"] <= 15 or row["sentence_id"] in sentences:
                    continue
                sentences.add(row["sentence_id"])
                out.append((row, _pcm(tar.extractfile(member).read())))
                if len(out) == n:
                    return out
    raise SystemExit(f"{lang}: only {len(out)} usable clips in the {SPLIT} split, {n} wanted")


def _pcm(wav_bytes: bytes) -> np.ndarray:
    """FLEURS WAVs are 32-bit float, which the wave module cannot read; ffmpeg decodes and resamples."""
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-"],
                          input=wav_bytes, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768


def _write(path: Path, x: np.ndarray) -> None:
    peak = float(np.max(np.abs(x))) or 1.0
    x = x / peak * 0.9 if peak > 0.9 else x
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(RATE)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2))) or 1e-9


def _at_snr(speech: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    noise = np.resize(noise, speech.shape)
    return speech + noise * (_rms(speech) / _rms(noise)) / (10 ** (snr_db / 20))


def _colored(kind: str, n: int, rng: np.random.Generator) -> np.ndarray:
    proc = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                           f"anoisesrc=color={kind}:sample_rate={RATE}:seed={int(rng.integers(1 << 30))}:d={n / RATE}",
                           "-f", "s16le", "-ac", "1", "-"], capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768


def _babble(pool: list[np.ndarray], n: int, rng: np.random.Generator) -> np.ndarray:
    picks = rng.choice(len(pool), size=BABBLE_SPEAKERS, replace=False)
    mix = sum(np.resize(pool[i] / _rms(pool[i]), n) for i in picks)
    return mix / BABBLE_SPEAKERS


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-language", type=int, default=25, help="distinct sentences per language")
    ap.add_argument("--no-speech", type=int, default=10, help="clips per no-speech kind")
    args = ap.parse_args()

    rng = np.random.default_rng(SEED)
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    items, babble_pool = [], []
    for fleurs_lang, code in LANGUAGES.items():
        chosen = _first_wavs(fleurs_lang, {r["file"]: r for r in _tsv(fleurs_lang)}, args.per_language + BABBLE_SPEAKERS)
        speech, babble_src = chosen[:args.per_language], chosen[args.per_language:]
        babble_pool += [x for _, x in babble_src]
        print(f"{fleurs_lang}: {len(speech)} sentences, {len(babble_src)} babble speakers")
        for r, x in speech:
            for condition in ("clean", "pink", "babble"):
                y = x if condition == "clean" else _at_snr(
                    x, _colored("pink", len(x), rng) if condition == "pink" else _babble(babble_pool, len(x), rng), SNR_DB)
                item_id = f"{code}_{Path(r['file']).stem}_{condition}"
                _write(audio_dir / f"{item_id}.wav", y)
                items.append({"id": item_id, "kind": "speech", "language": code, "condition": condition,
                              "reference": r["normalized"], "source": f"fleurs/{fleurs_lang}/{SPLIT}/{r['file']}"})
    for kind in ("pink", "brown", "babble"):
        for i in range(args.no_speech):
            n = int(rng.integers(5, 13)) * RATE
            x = _babble(babble_pool, n, rng) * 0.3 if kind == "babble" else _colored(kind, n, rng) * 0.3
            item_id = f"none_{kind}_{i:02d}"
            _write(audio_dir / f"{item_id}.wav", x)
            items.append({"id": item_id, "kind": "no_speech", "language": None, "condition": kind,
                          "reference": None, "source": "generated"})

    with open(ROOT / "manifest.jsonl", "w") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"{len(items)} items -> {ROOT / 'manifest.jsonl'}")


if __name__ == "__main__":
    main()
