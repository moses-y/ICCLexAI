import { useState } from 'react'
import { api, ApiError, type CaseDetail, type CustodyView, type Finding, type PackageResult, type Session } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }

const CHECKLIST = [
  'Unzip the package and open README_FIRST.txt.',
  'Check each file’s SHA-256 against manifest.json (sha256sum on Linux and macOS, Get-FileHash on Windows).',
  'Open https://otplink.icc-cpi.int in a browser you trust. Consider a private window and a network you trust.',
  'Choose anonymous or named submission, whichever is safe for you.',
  'Copy each heading from otplink_fields.md into the matching OTPLink field. OTPLink’s form may differ from our provisional map: follow the live form.',
  'Upload the files in the order listed in otplink_fields.md.',
  'Keep any reference OTPLink gives you, and record it below.',
]

export default function PackagePanel({ session, detail, findings, refresh }: Props) {
  const [strip, setStrip] = useState(false)
  const [result, setResult] = useState<PackageResult | null>(null)
  const [custody, setCustody] = useState<CustodyView | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ref, setRef] = useState('')

  const confirmed = findings.filter(f => f.status === 'confirmed' || f.status === 'edited').length
  const unreviewed = findings.filter(f => f.status === 'proposed').length
  const analysing = detail.status === 'analysing'
  const filed = detail.status === 'filed_by_user'

  const wrap = async (fn: () => Promise<void>) => {
    setBusy(true); setError(null)
    try { await fn() } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  const build = () => wrap(async () => { setResult(await api.buildPackage(session, strip)); setCustody(await api.custody(session)); await refresh() })
  const download = () => wrap(async () => {
    const blob = await api.downloadPackage(session)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `icclex_package_v${detail.package?.version ?? 1}.zip`; a.click()
    URL.revokeObjectURL(url)
  })
  const markFiled = () => wrap(async () => { await api.markFiled(session, ref.trim() || undefined); await refresh() })

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base">Build your package</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>{confirmed} confirmed finding{confirmed === 1 ? '' : 's'} will go in. {unreviewed > 0 && <strong>{unreviewed} you have not reviewed will be left out.</strong>}</p>
          <label className="flex gap-2"><input type="checkbox" checked={strip} onChange={e => setStrip(e.target.checked)} className="mt-1" />
            <span>Remove hidden metadata (camera, GPS, time) from the copies in the package. Works for JPEG and PNG only; other files go in unchanged. Your stored originals are never changed. Removing it can make the files harder to verify, so the ICC may prefer them intact: decide with your safety in mind.</span></label>
          <Button onClick={() => void build()} disabled={busy || analysing || confirmed === 0 || filed}>{detail.package ? 'Rebuild package' : 'Build package'}</Button>
          {analysing && <p>Files are still being analysed.</p>}
          {confirmed === 0 && !analysing && <p className="text-gray-600">Confirm at least one finding on the Review step first.</p>}
          {error && <p role="alert" className="text-red-700">{error}</p>}
          {result && (
            <div className="rounded bg-green-50 p-2">
              <p>Package version {result.version} built. {result.narrative_model ? `The account was drafted by ${result.narrative_model} from your confirmed findings.` : 'The account is a plain list of your confirmed findings, each marked with where it came from.'}</p>
              {result.removed_from_draft.length > 0 && <details className="mt-1"><summary>{result.removed_from_draft.length} draft item(s) were removed</summary>
                <ul className="list-disc pl-5">{result.removed_from_draft.map((d, i) => <li key={i}>“{d.text}” — {d.reason}</li>)}</ul></details>}
            </div>
          )}
          {detail.package?.status === 'stale' && <p className="rounded bg-amber-50 p-2">You changed a finding after building. Rebuild before you download.</p>}
          {detail.package?.status === 'current' && <Button variant="outline" onClick={() => void download()} disabled={busy}>Download package (.zip)</Button>}
          {custody && <p className="text-xs text-gray-600">Custody log: {custody.events.length} events, chain {custody.chain_valid ? 'verified' : `BROKEN (${custody.problem})`}.</p>}
        </CardContent>
      </Card>

      {detail.package?.status === 'current' && (
        <Card>
          <CardHeader><CardTitle className="text-base">File it on OTPLink</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Nothing has been sent to the ICC.</strong> You file the package yourself. Sending it does not open a case: the Prosecutor decides what to do with information received.</p>
            <ol className="list-decimal space-y-1 pl-5">{CHECKLIST.map(c => <li key={c}>{c}</li>)}</ol>
            {!filed ? (
              <div className="border-t pt-2">
                <label className="block text-xs">Once you have filed it: any reference OTPLink gave you (optional)
                  <input value={ref} onChange={e => setRef(e.target.value)} className="mt-0.5 w-full rounded border px-2 py-1 text-sm" /></label>
                <Button className="mt-2" onClick={() => void markFiled()} disabled={busy}>I have filed this on OTPLink</Button>
                <p className="mt-1 text-xs text-gray-600">This only records what you tell us; we cannot check it.</p>
              </div>
            ) : <p className="rounded bg-green-50 p-2">Recorded as filed by you{detail.otp_reference ? `. Reference: ${detail.otp_reference}` : ''}.</p>}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
