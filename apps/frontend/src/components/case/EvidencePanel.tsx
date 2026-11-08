import { useEffect, useRef, useState } from 'react'
import { api, ApiError, type CaseDetail, type EvidenceItem, type Session, type UploadResult } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { AlertTriangle, ArrowRight, CheckCircle2, CircleDashed, FileUp, Loader2, UploadCloud } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props { session: Session; detail: CaseDetail; refresh: () => Promise<void>; next: () => void }

const AGENT_LABEL: Record<string, string> = {
  metadata: 'File details', geolocation: 'Location', visual: 'What it shows', audio_video: 'Speech', document: 'Document text', integrity: 'Checks',
}

function Preview({ session, ev }: { session: Session; ev: EvidenceItem }) {
  const [url, setUrl] = useState<string | null>(null)
  useEffect(() => {
    if (!/^(image|video|audio)\//.test(ev.mime)) return
    let made: string | null = null
    let cancelled = false
    api.evidenceBlob(session, ev.id).then(b => { if (!cancelled) { made = URL.createObjectURL(b); setUrl(made) } }).catch(() => undefined)
    return () => { cancelled = true; if (made) URL.revokeObjectURL(made) }
  }, [session, ev.id, ev.mime])
  if (!url) return null
  if (ev.mime.startsWith('image/')) return <img src={url} alt={ev.original_name} className="max-h-40 rounded-lg ring-1 ring-border" />
  if (ev.mime.startsWith('video/')) return <video src={url} controls className="max-h-40 rounded-lg ring-1 ring-border" />
  return <audio src={url} controls />
}

export function jobBadge(status: string) {
  const cls = status === 'done' ? 'bg-brand-teal/10 text-brand-teal' : status === 'failed' ? 'bg-red-100 text-red-900' : 'bg-secondary text-brand-navy'
  const Icon = status === 'done' ? CheckCircle2 : status === 'failed' ? AlertTriangle : status === 'running' ? Loader2 : CircleDashed
  return <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}><Icon className={`h-3 w-3 ${status === 'running' ? 'animate-spin' : ''}`} />{status === 'failed' ? 'not analysed' : status}</span>
}

export default function EvidencePanel({ session, detail, refresh, next }: Props) {
  const input = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [rejected, setRejected] = useState<UploadResult[]>([])
  const [error, setError] = useState<string | null>(null)

  const upload = async (files: FileList | null) => {
    if (!files?.length) return
    setBusy(true); setError(null)
    try {
      const r = await api.upload(session, Array.from(files))
      setRejected(r.results.filter(x => x.error))
      await refresh()
    } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false); if (input.current) input.current.value = '' }
  }

  const consentToggle = async () => { await api.updateCase(session, { external_processing_consent: !detail.external_processing_consent }); await refresh() }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="text-base"><FileUp />Add your files</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>Photos, video, audio and documents. Your original files are kept exactly as you send them; each one gets a fingerprint (SHA-256) the moment it arrives.</p>
          <label className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-brand-teal/30 bg-accent/50 px-4 py-6 text-center transition-colors hover:border-brand-teal/60 hover:bg-accent">
            {busy ? <Loader2 className="h-8 w-8 animate-spin text-brand-teal" /> : <UploadCloud className="h-8 w-8 text-brand-teal" />}
            <span className="font-medium text-brand-navy">{busy ? 'Uploading…' : 'Choose files to add'}</span>
            <span className="text-xs text-muted-foreground">Photos, video, audio, documents</span>
            <input ref={input} type="file" multiple className="sr-only" onChange={e => void upload(e.target.files)} disabled={busy || detail.status === 'filed_by_user'} aria-label="Choose files" />
          </label>
          {error && <p role="alert" className="text-red-700">{error}</p>}
          {rejected.map(r => <p key={r.original_name} role="alert" className="text-red-700">{r.original_name}: {r.error}</p>)}
          <label className="flex items-center gap-2 border-t pt-2">
            <input type="checkbox" checked={detail.external_processing_consent} onChange={() => void consentToggle()} />
            <span>Allow outside services (AI provider, OpenStreetMap) to analyse content. Applies to files analysed from now on.</span>
          </label>
        </CardContent>
      </Card>

      {detail.evidence.map(ev => (
        <Card key={ev.id}>
          <CardContent className="space-y-2 pt-4 text-sm">
            <div className="flex flex-wrap items-start gap-4">
              <Preview session={session} ev={ev} />
              <div className="min-w-0 flex-1">
                <p className="font-medium text-brand-navy">{ev.original_name}</p>
                <p className="break-all text-xs text-muted-foreground">{ev.mime} · {ev.size_bytes.toLocaleString()} bytes · SHA-256 {ev.sha256}</p>
                <ul className="mt-2 space-y-1">
                  {ev.jobs.map(j => (
                    <li key={j.agent} className="flex flex-wrap items-center gap-1">
                      {jobBadge(j.status)} <span className="ml-1">{AGENT_LABEL[j.agent] ?? j.agent}</span>
                      {j.error && <span className="ml-2 text-xs text-muted-foreground">— {j.error}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      {detail.evidence.length > 0 && <Button onClick={next} disabled={detail.status === 'analysing'}>{detail.status === 'analysing' ? 'Analysing…' : <>Review what was found<ArrowRight /></>}</Button>}
    </div>
  )
}
