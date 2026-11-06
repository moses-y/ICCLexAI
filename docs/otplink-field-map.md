# OTPLink field map (provisional)

OTPLink (https://otplink.icc-cpi.int) is the ICC Office of the Prosecutor's electronic channel for
information from victims, witnesses and civil society. It has no public API and no published terms
allowing automated submission, so ICCLexAI prepares a package and the person files it.

**Status: not verified against the live form.** The ICC's own site refused automated fetches while this
was researched (2026-11-05), so everything below comes from a 2023 article and the portal's landing
page. `otplink_fields.md` in each package repeats this caveat. Someone has to walk through the form
once and fill in the last column.

| What we believe | Source | Verified on the live form |
|---|---|---|
| Launched 24 May 2023; replaced older channels | Just Security, "Digital evidence collection at the ICC" (justsecurity.org/87149) | not yet |
| Anonymous submission is allowed, or give name and contact details | same | not yet |
| Describe the incident: its name and date | same | not yet |
| Mark the location on an interactive map | same | not yet |
| Up to about 1,000 files and about 4 GB per submission (2023) | same | not yet |
| English only | same | not yet |
| Accepted file types | not found | not yet |
| Required versus optional fields, character limits | not found | not yet |
| Whether a confirmation or reference number is issued, and its format | not found | not yet |
| Postal alternative: PO Box 19519, 2500 CM The Hague | Coalition for the ICC | not yet |

## To do before relying on `otplink_fields.md`

1. Open the form (a private window; nothing needs to be submitted) and list every field, in order, with limits.
2. Record the accepted file types and size limits, and set `MAX_UPLOAD_BYTES` in `apps/backend/icclex/config.py` to match.
3. Update the headings in `build_package` (`apps/backend/icclex/package.py`, the `fields` text) to match the form.
4. Read the Eurojust / ICC-OTP guidelines *Documenting international crimes and human rights violations for accountability purposes* (2022) and copy its chain-of-custody annex's columns into `custody_log.csv`. The PDF could not be retrieved during research.
5. Ask the OTP whether metadata should be left intact, and whether AI-assisted descriptions are acceptable. No guidance on either was found.
