# OTPLink field map

OTPLink (https://otplink.icc-cpi.int) is the ICC Office of the Prosecutor's electronic channel for
information from victims, witnesses and civil society. It has no public API and no published terms
allowing automated submission, so ICCLexAI prepares a package and the person files it.

**Status: fields and limits checked against the live form on 2026-11-06.** The page is a JavaScript
app, so plain fetches return only a browser-compatibility notice; it was rendered with headless
Chromium (`chromium --headless --dump-dom https://otplink.icc-cpi.int`). Nothing was submitted, so
what happens after Submit is still unknown.

| Field, in form order | Live form, 2026-11-06 |
|---|---|
| Investigation | required dropdown (the situation); ICCLexAI does not choose it |
| Contact Name / Contact Email / Contact Phone | required unless anonymous; name max 100 chars, email max 500, phone defaults to +31 |
| "I want to make this submission anonymously" | checkbox |
| Incident Name | required, max 100 characters |
| Factual Summary | required rich-text box, max 1.8 MB |
| Date of Incident | required, Start Date and End Date |
| Language of the Item | required dropdown |
| Location of Incident | required, place search plus a draggable map pin |
| Add Attachment(s) | each file under 2.0 GB, submission under 4.0 GB, at most 1000 files |
| Submit | behind reCAPTCHA; the form asks that no VPN or proxy is used |

Accepted file types (the upload input's `accept` list) include common photo, RAW, video, audio,
office, PDF, e-mail (`.eml`, `.msg`), web-archive (`.mht`), GPS (`.gpx`) and forensic-image (`.e01`)
formats. Interface language was English; a "How to translate the website" link is offered.

`apps/backend/icclex/package.py` uses these headings and limits (`OTPLINK_*` constants) and warns in
`otplink_fields.md` when a case exceeds them.

Still unknown:

| Question | Status |
|---|---|
| Whether a confirmation or reference number is issued, and its format | not checked: needs a real submission |
| Postal alternative: PO Box 19519, 2500 CM The Hague (Coalition for the ICC) | not re-checked |

## To do before relying on `otplink_fields.md`

1. ~~List every field with limits; match `MAX_UPLOAD_BYTES` and the `build_package` headings.~~ Done 2026-11-06.
2. Re-check the form before each release; it can change without notice.
3. Read the Eurojust / ICC-OTP guidelines *Documenting international crimes and human rights violations for accountability purposes* (2022) and copy its chain-of-custody annex's columns into `custody_log.csv`. The PDF could not be retrieved during research.
4. Ask the OTP whether metadata should be left intact, and whether AI-assisted descriptions are acceptable. No guidance on either was found.
