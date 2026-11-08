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
import SendPanel from './SendPanel'
import { basicsComplete } from './IncidentBasics'
import { ArrowRight, Check, FolderUp, KeyRound, LogOut, PackageCheck, PenLine, Scale, ScanSearch, Send, ShieldCheck, type LucideIcon } from 'lucide-react'

const STEPS: readonly { id: string; label: string; icon: LucideIcon }[] = [
  { id: 'evidence', label: 'Files', icon: FolderUp },
  { id: 'review', label: 'Review', icon: ScanSearch },
  { id: 'account', label: 'Your account', icon: PenLine },
  { id: 'package', label: 'Prepare', icon: PackageCheck },
  { id: 'send', label: 'Send', icon: Send },
] as const
type Step = 'evidence' | 'review' | 'account' | 'package' | 'send'
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
    <div className="mx-auto max-w-2xl space-y-5 p-4 pt-10">
      <div className="brand-gradient overflow-hidden rounded-2xl p-6 text-white shadow-lg shadow-brand-navy/20">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-white/15 ring-1 ring-white/25"><Scale className="h-6 w-6" /></span>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">ICCLexAI</h1>
            <p className="text-sm text-white/75">Prepare evidence for the ICC Office of the Prosecutor</p>
          </div>
        </div>
      </div>
      <p className="text-sm text-muted-foreground">
        This tool helps you prepare information for the International Criminal Court’s Office of the Prosecutor.
        It analyses your files, shows you what it found, and builds a package <strong>that you file yourself</strong> on
        the ICC’s OTPLink portal. It never submits anything for you, and it does not give legal advice or decide
        whether a crime was committed.
      </p>
      <Card>
        <CardHeader><CardTitle className="text-base"><ShieldCheck />Before you start</CardTitle></CardHeader>
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
          <Button onClick={create} disabled={busy}>Start a new case<ArrowRight /></Button>
          <div className="border-t pt-3">
            <label className="flex items-center gap-1.5 text-xs text-muted-foreground"><KeyRound className="h-3.5 w-3.5" />Already have a case key?</label>
            <div className="flex gap-2">
              <input value={resumeText} onChange={e => setResumeText(e.target.value)} className="flex-1 rounded-lg border px-3 py-1.5 text-sm" placeholder="paste your case key" />
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
      <header className="brand-gradient flex flex-wrap items-center justify-between gap-3 rounded-2xl px-5 py-4 text-white shadow-lg shadow-brand-navy/20">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-white/15 ring-1 ring-white/25"><Scale className="h-5 w-5" /></span>
          <div>
            <h1 className="text-lg font-semibold leading-tight tracking-tight">ICCLexAI</h1>
            <p className="text-xs text-white/75">Case {detail.id.slice(0, 8)} · <span className="rounded-full bg-brand-gold/25 px-2 py-0.5 text-white ring-1 ring-brand-gold/40">{detail.status.replace(/_/g, ' ')}</span></p>
          </div>
        </div>
        <Button variant="light" size="sm" onClick={leave}><LogOut />Close this case on this device</Button>
      </header>
      <details className="rounded-xl border border-brand-gold/40 bg-brand-gold/10 p-3 text-sm" open={!stored}>
        <summary className="flex cursor-pointer items-center gap-2 font-medium text-brand-navy"><KeyRound className="h-4 w-4 text-brand-gold" />Your case key{!stored && ' (this browser could not save it: copy it now)'}</summary>
        <p className="mt-2 break-all rounded-lg bg-white/70 p-2 font-mono text-xs">{toKeyString(session)}</p>
        <p className="mt-1 text-xs text-muted-foreground">Anyone with this key can open your case. Closing the case here removes it from this device only; use the key to open it again. If you lose the key, the case cannot be recovered.</p>
      </details>
      {error && <p role="alert" className="rounded-lg bg-red-50 p-2 text-sm text-red-800">{error}</p>}

      <nav className="flex gap-1 overflow-x-auto rounded-xl border bg-white/80 p-1.5 shadow-sm backdrop-blur" aria-label="Steps">
        {STEPS.map((s, i) => {
          const at = STEPS.findIndex(x => x.id === step)
          const current = s.id === step
          const Icon = i < at ? Check : s.icon
          return (
            <button key={s.id} type="button" onClick={() => go(s.id as Step)} aria-current={current ? 'step' : undefined}
              className={`flex min-w-fit flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                current ? 'bg-gradient-to-r from-brand-navy to-brand-teal text-white shadow-md shadow-brand-navy/25'
                  : i < at ? 'text-brand-teal hover:bg-accent' : 'text-muted-foreground hover:bg-secondary hover:text-brand-navy'}`}>
              <span className={`grid h-6 w-6 place-items-center rounded-full text-xs ${current ? 'bg-white/20' : i < at ? 'bg-brand-teal/10' : 'bg-secondary'}`}><Icon className="h-3.5 w-3.5" /></span>
              <span><span className="opacity-60">{i + 1} · </span>{s.label}</span>
            </button>
          )
        })}
      </nav>

      {step === 'evidence' && <EvidencePanel session={session} detail={detail} refresh={refresh} next={() => go('review')} />}
      {step === 'review' && (<>
        <FindingsPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <MapPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => go('account')}>Continue to your account<ArrowRight /></Button>
          {unreviewed > 0 && <span className="text-sm text-muted-foreground">{unreviewed} not reviewed yet: they stay out of the package until you confirm them.</span>}
        </div>
      </>)}
      {step === 'account' && (<>
        <StatementsPanel session={session} detail={detail} findings={findings} refresh={refresh} />
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => go('package')} disabled={!basicsComplete(detail)}>Continue to prepare<ArrowRight /></Button>
          {!basicsComplete(detail) && <span className="text-sm text-muted-foreground">Give the date and place first: OTPLink requires both.</span>}
        </div>
      </>)}
      {step === 'package' && (<>
        <PackagePanel session={session} detail={detail} findings={findings} refresh={refresh} />
        {detail.package?.status === 'current' && <div><Button onClick={() => go('send')}>Continue to send<ArrowRight /></Button></div>}
      </>)}
      {step === 'send' && <SendPanel session={session} detail={detail} refresh={refresh} />}
    </div>
  )
}
