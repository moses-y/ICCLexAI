import { useState } from 'react'
import { api, ApiError, type CaseDetail, type CustodyView, type Finding, type PackageResult, type Session } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { AlertTriangle, CheckCircle2, Download, PackageCheck, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { basicsComplete } from './IncidentBasics'

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }


export default function PackagePanel({ session, detail, findings, refresh }: Props) {
  const [consent, setConsent] = useState(false)
  const [result, setResult] = useState<PackageResult | null>(null)
  const [custody, setCustody] = useState<CustodyView | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const confirmed = findings.filter(f => f.status === 'confirmed' || f.status === 'edited').length
  const unreviewed = findings.filter(f => f.status === 'proposed').length
  const analysing = detail.status === 'analysing'
  const filed = detail.status === 'filed_by_user'
  const sourced = new Set(findings.filter(f => f.kind === 'stated_fact' && f.evidence_id && f.status !== 'rejected').map(f => f.evidence_id))
  const unsourced = detail.evidence.filter(e => !sourced.has(e.id)).length
  const checks = [
    { label: detail.incident_from ? `When: ${detail.incident_from}${detail.incident_to && detail.incident_to !== detail.incident_from ? ` to ${detail.incident_to}` : ''}` : 'When it happened: not given (Your account step)', ok: Boolean(detail.incident_from), required: true },
    { label: detail.incident_location_text ? `Where: ${detail.incident_location_text}` : 'Where it happened: not given (Your account step)', ok: Boolean(detail.incident_location_text), required: true },
    { label: unsourced ? `${unsourced} file(s) without a note on where they came from` : 'Where each file came from: given', ok: unsourced === 0, required: false },
    { label: `${confirmed} confirmed finding${confirmed === 1 ? '' : 's'} will go in${unreviewed ? `; ${unreviewed} not reviewed will be left out` : ''}`, ok: confirmed > 0, required: true },
  ]

  const wrap = async (fn: () => Promise<void>) => {
    setBusy(true); setError(null)
    try { await fn() } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  const build = () => wrap(async () => { setResult(await api.buildPackage(session, consent)); setCustody(await api.custody(session)); await refresh() })
  const download = () => wrap(async () => {
    const blob = await api.downloadPackage(session)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `icclex_package_v${detail.package?.version ?? 1}.zip`; a.click()
    URL.revokeObjectURL(url)
  })

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base"><PackageCheck />Prepare your submission</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <ul className="space-y-1.5 rounded-lg bg-secondary/60 p-3">
            {checks.map(c => {
              const Icon = c.ok ? CheckCircle2 : c.required ? XCircle : AlertTriangle
              return <li key={c.label} className="flex items-start gap-2"><Icon className={`mt-0.5 h-4 w-4 shrink-0 ${c.ok ? 'text-brand-teal' : c.required ? 'text-red-600' : 'text-amber-600'}`} />{c.label}</li>
            })}
          </ul>
          <label className="flex gap-2 rounded-lg border border-brand-gold/40 bg-brand-gold/10 p-3"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} className="mt-1" />
            <span>I agree to send my files exactly as I uploaded them, including hidden details such as when, where and on what device they were made. These details help show the files are genuine.</span></label>
          <Button onClick={() => void build()} disabled={busy || analysing || confirmed === 0 || filed || !consent || !basicsComplete(detail)}>{detail.package ? 'Prepare again' : 'Prepare my submission'}</Button>
          {analysing && <p>Files are still being analysed.</p>}
          {confirmed === 0 && !analysing && <p className="text-muted-foreground">Confirm at least one finding on the Review step first.</p>}
          {error && <p role="alert" className="text-red-700">{error}</p>}
          {result && (
            <div className="rounded-lg border border-brand-teal/20 bg-brand-teal/5 p-3">
              <p>Package version {result.version} built. {result.narrative_model ? `The account was drafted by ${result.narrative_model} from your confirmed findings.` : 'The account is a plain list of your confirmed findings, each marked with where it came from.'}</p>
              {result.removed_from_draft.length > 0 && <details className="mt-1"><summary>{result.removed_from_draft.length} draft item(s) were removed</summary>
                <ul className="list-disc pl-5">{result.removed_from_draft.map((d, i) => <li key={i}>“{d.text}” — {d.reason}</li>)}</ul></details>}
            </div>
          )}
          {detail.package?.status === 'stale' && <p className="rounded bg-amber-50 p-2">You changed a finding after building. Prepare it again.</p>}
          {detail.package?.status === 'current' && <Button variant="outline" onClick={() => void download()} disabled={busy}><Download />Save a copy for your records (.zip)</Button>}
          {custody && <p className="text-xs text-muted-foreground">Custody log: {custody.events.length} events, chain {custody.chain_valid ? 'verified' : `BROKEN (${custody.problem})`}.</p>}
        </CardContent>
      </Card>

    </div>
  )
}
