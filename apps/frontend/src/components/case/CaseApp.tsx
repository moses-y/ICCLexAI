import { useCallback, useEffect, useRef, useState } from 'react'
import { api, ApiError, type CaseDetail, type Finding, type Session } from '@/lib/api'
import { forgetSession, loadSession, parseKeyString, saveSession, toKeyString } from '@/lib/session'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import EvidencePanel from './EvidencePanel'
import FindingsPanel from './FindingsPanel'
import StatementsPanel from './StatementsPanel'
import MapPanel from './MapPanel'
import PackagePanel from './PackagePanel'

const STEPS = [
  { id: 'evidence', label: '1 · Files' },
  { id: 'review', label: '2 · Review' },
  { id: 'account', label: '3 · Your account' },
  { id: 'package', label: '4 · Package' },
] as const
type Step = (typeof STEPS)[number]['id']
const POLL_MS = 2000

function StartScreen({ onSession }: { onSession: (s: Session) => void }) {
  const [consent, setConsent] = useState(false)
  const [resumeText, setResumeText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const create = async () => {
    setBusy(true); setError(null)
    try {
      const r = await api.createCase(consent)
      onSession({ caseId: r.case_id, token: r.token })
    } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  const resume = async () => {
    const s = parseKeyString(resumeText)
    if (!s) { setError('That does not look like a case key.'); return }
    try { await api.getCase(s); onSession(s) } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <h1 className="text-2xl font-bold">ICCLexAI</h1>
      <p className="text-sm text-gray-700">
        This tool helps you prepare information for the International Criminal Court’s Office of the Prosecutor.
        It analyses your files, shows you what it found, and builds a package <strong>that you file yourself</strong> on
        the ICC’s OTPLink portal. It never submits anything for you, and it does not give legal advice or decide
        whether a crime was committed.
      </p>
      <Card>
        <CardHeader><CardTitle className="text-base">Before you start</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>No account or name is needed. You get a <strong>case key</strong>. Keep it safe: there is no way to recover it.</p>
          <label className="flex gap-2">
            <input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} className="mt-1" />
            <span>
              Allow sending my files’ content to outside services to analyse them: images, audio and text go to an AI
              provider, and GPS points go to OpenStreetMap to find the place name. Leave this off to keep everything on
              this server; only the checks that read file details will run.
            </span>
          </label>
          <Button onClick={create} disabled={busy}>Start a new case</Button>
          <div className="border-t pt-3">
            <label className="block text-xs text-gray-600">Already have a case key?</label>
            <div className="flex gap-2">
              <input value={resumeText} onChange={e => setResumeText(e.target.value)} className="flex-1 rounded border px-2 py-1 text-sm" placeholder="paste your case key" />
              <Button variant="outline" onClick={resume}>Open</Button>
            </div>
          </div>
          {error && <p role="alert" className="text-red-700">{error}</p>}
        </CardContent>
      </Card>
    </div>
  )
}

export default function CaseApp() {
  const [session, setSession] = useState<Session | null>(() => loadSession())
  const [detail, setDetail] = useState<CaseDetail | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [step, setStep] = useState<Step>('evidence')
  const [error, setError] = useState<string | null>(null)
  const [stored, setStored] = useState(true)
  const timer = useRef<number>()

  const refresh = useCallback(async () => {
    if (!session) return
    try {
      const [d, f] = await Promise.all([api.getCase(session), api.findings(session)])
      setDetail(d); setFindings(f); setError(null)
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) { forgetSession(); setSession(null); setDetail(null) }
      else setError(e instanceof ApiError ? e.message : String(e))
    }
  }, [session])

  useEffect(() => { void refresh() }, [refresh])
  useEffect(() => {
    window.clearInterval(timer.current)
    if (session && detail?.status === 'analysing') timer.current = window.setInterval(() => void refresh(), POLL_MS)
    return () => window.clearInterval(timer.current)
  }, [session, detail?.status, refresh])

  const begin = (s: Session) => { setStored(saveSession(s)); setSession(s) }
  // Only the Files step had a "next" button; after Review the way on was the tabs at the top of a long page.
  const go = (to: Step) => { setStep(to); window.scrollTo({ top: 0 }) }
  const unreviewed = findings.filter(f => f.status === 'proposed').length
  const leave = () => { forgetSession(); setSession(null); setDetail(null); setFindings([]); setStep('evidence') }

  if (!session) return <StartScreen onSession={begin} />
  if (!detail) return <p className="p-4 text-sm">{error ?? 'Loading your case…'}</p>

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-4">
      <header className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-bold">ICCLexAI <span className="text-sm font-normal text-gray-600">· case {detail.id.slice(0, 8)} · {detail.status.replace(/_/g, ' ')}</span></h1>
        <Button variant="outline" size="sm" onClick={leave}>Close this case on this device</Button>
      </header>
      <details className="rounded border bg-amber-50 p-2 text-sm" open={!stored}>
        <summary className="cursor-pointer font-medium">Your case key{!stored && ' (this browser could not save it: copy it now)'}</summary>
        <p className="mt-1 break-all font-mono text-xs">{toKeyString(session)}</p>
        <p className="mt-1 text-xs text-gray-700">Anyone with this key can open your case. Closing the case here removes it from this device only; use the key to open it again. If you lose the key, the case cannot be recovered.</p>
      </details>
      {error && <p role="alert" className="rounded bg-red-50 p-2 text-sm text-red-800">{error}</p>}

      <nav className="flex gap-1 overflow-x-auto" aria-label="Steps">
        {STEPS.map(s => (
          <Button key={s.id} size="sm" variant={s.id === step ? 'default' : 'outline'} onClick={() => go(s.id)}>{s.label}</Button>
        ))}
      </nav>

      {step === 'evidence' && <EvidencePanel session={session} detail={detail} refresh={refresh} next={() => go('review')} />}
      {step === 'review' && (<>
        <FindingsPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <MapPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => go('account')}>Continue to your account</Button>
          {unreviewed > 0 && <span className="text-sm text-gray-700">{unreviewed} not reviewed yet: they stay out of the package until you confirm them.</span>}
        </div>
      </>)}
      {step === 'account' && (<>
        <StatementsPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <div><Button onClick={() => go('package')}>Continue to the package</Button></div>
      </>)}
      {step === 'package' && <PackagePanel session={session} detail={detail} findings={findings} refresh={refresh} />}
    </div>
  )
}
