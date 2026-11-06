# Case building workflow

Rewritten 2026-11-06. The earlier version of this file described a flow that ended with the AI
"automatically submitting to the ICC review queue" and a generated case reference. That step was
simulated in the browser (a timer and `Math.random()`); nothing was ever sent. The workflow below is
what the system actually does. Design and schema: [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).

## Steps

1. **Start a case.** No account. You get a case key (keep it: it cannot be recovered). Choose whether outside services may analyse your content.
2. **Add files.** Each original is stored untouched, read-only, with a SHA-256 taken as it arrives. Its type is read from its bytes, not its name.
3. **Analysis.** Agents run in the background and each file shows what ran, what failed and why:
   - *File details*: capture time, GPS, device, from the file itself.
   - *Location*: the place name for the GPS point, possible places from visible clues, and a warning if the file's GPS is far from where you say it happened.
   - *What it shows*, *speech*, *document text*: need a model and your consent.
   - *Checks*: metadata consistency. A flag means "worth checking", never "tampered".
4. **Review.** Every finding is labelled **From the file**, **AI suggestion** or **Your words**. Confirm, edit or reject each. Unreviewed findings never go into the package.
5. **Your account.** Talk to the interviewer (needs consent and a model) or write statements yourself. If a date you give disagrees with a file's capture date, you are asked which is right.
6. **Build the package.** A ZIP with your originals (optionally metadata-stripped copies for JPEG and PNG), a manifest of SHA-256 hashes, a summary PDF, a GeoJSON of confirmed locations, the custody log, and text for each OTPLink field. Every sentence of the account cites a confirmed finding.
7. **File it yourself** on OTPLink using the checklist. Then tell the app you did, with any reference you were given. That is recorded as your statement, not verified.

If you change a finding after building, the package becomes stale and must be rebuilt.
