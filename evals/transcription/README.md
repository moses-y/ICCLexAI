# Transcription evaluation

Checks that the transcription step keeps real speech and withholds invented text.

On 2026-11-06 Whisper turned two Nairobi street clips into Spanish ("¡Adiós!") and Malay
("Terima kasih"), and noisy Swahili into Greek letters. The agent now keeps a transcript only in an
expected language (`ICCLEX_SPEECH_LANGUAGES`) above a confidence floor (`TRANSCRIBE_MIN_LOGPROB`,
`TRANSCRIBE_FORCED_MIN_LOGPROB` in `apps/backend/icclex/config.py`). This evaluation is where those
floors are set and re-checked.

```bash
python evals/transcription/build.py --per-language 25   # ~10 MB per language from FLEURS, about 2 min
python evals/transcription/run.py                       # calls Whisper for anything not cached, then reports
python evals/transcription/run.py --offline             # re-report from the cache, no model calls
```

Run it again when the transcription model, the floors or the expected languages change.

## What is in the set

| Kind | Source | Counts as a failure when |
|---|---|---|
| Speech, Swahili and English | FLEURS `dev` split (`sw_ke`, `en_us`), one clip per sentence | withheld, or kept with word error rate above 0.5 |
| Same speech with noise | pink noise and 6-speaker crowd babble at 5 dB SNR | as above |
| No speech | pink noise, brown noise, crowd babble alone | any transcript is kept |

Everything lives in `var/eval/transcription/`, which git ignores. Cached replies are kept per model,
so changing the model re-measures from scratch.

## Limits

- FLEURS is read speech recorded indoors. The noise is added afterwards, which approximates street
  footage but is not the same thing.
- There is no Sheng. Real field recordings and Sheng need labelling by someone who speaks it; add them
  to `manifest.jsonl` with `"kind": "speech"` and a `reference` transcript, or `"kind": "no_speech"`.
- Whisper's output varies a little between runs, so treat a single run's percentages as approximate.
