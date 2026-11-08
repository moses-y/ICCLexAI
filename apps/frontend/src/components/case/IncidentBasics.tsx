import { useState } from 'react'
import { api, ApiError, type CaseDetail, type Finding, type Session } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { CalendarDays, MapPin } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// OTPLink requires a date and a place, and the first real package (2026-11-06) reached it with both "not stated"
// because nothing asked for them. The files often hint at both; the person decides.

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }

const DATE_HINT: Record<string, string> = {
  capture_time: 'recorded in the file', name_date: 'in a file name, when an app saved it',
}

function dateHints(findings: Finding[]) {
  const seen = new Map<string, string>()
  for (const f of findings) {
    const iso = typeof f.value.iso === 'string' ? f.value.iso.slice(0, 10) : null
    if (iso && DATE_HINT[f.kind] && f.status !== 'rejected' && !seen.has(iso)) seen.set(iso, DATE_HINT[f.kind])
  }
  return [...seen].map(([date, why]) => ({ date, why }))
}

function placeHints(findings: Finding[]) {
  const out: { text: string; why: string }[] = []
  for (const f of findings) {
    if (f.status === 'rejected') continue
    if (f.kind === 'place' && f.value.display_name) out.push({ text: String(f.value.display_name), why: 'from GPS in a file' })
    if (f.kind === 'place_candidate' && f.value.place) out.push({ text: String(f.value.place), why: 'AI suggestion from what is visible' })
  }
  return out.filter((h, i) => out.findIndex(o => o.text === h.text) === i)
}

export function basicsComplete(detail: CaseDetail) {
  return Boolean(detail.incident_from && detail.incident_location_text)
}

export default function IncidentBasics({ session, detail, findings, refresh }: Props) {
  const [name, setName] = useState(detail.incident_name ?? '')
  const [from, setFrom] = useState(detail.incident_from ?? '')
  const [to, setTo] = useState(detail.incident_to ?? '')
  const [place, setPlace] = useState(detail.incident_location_text ?? '')
  const [sources, setSources] = useState<Record<string, { kind: 'self' | 'other'; from: string; link: string }>>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wrap = async (fn: () => Promise<void>) => {
    setBusy(true); setError(null)
    try { await fn() } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  const save = () => wrap(async () => {
    await api.updateCase(session, { incident_name: name || null, incident_from: from || null, incident_to: to || from || null,
                                    incident_location_text: place || null })
    await refresh()
  })
  const sourceOf = (evidenceId: string) =>
    findings.find(f => f.kind === 'stated_fact' && f.evidence_id === evidenceId && f.status !== 'rejected')
  const saveSource = (evidenceId: string) => wrap(async () => {
    const s = sources[evidenceId]
    if (!s) return
    const text = s.kind === 'self' ? 'I recorded this file myself.'
      : `I got this file from ${s.from.trim() || 'someone else'}${s.link.trim() ? ` (${s.link.trim()})` : ''}.`
    await api.addFact(session, { text, evidence_id: evidenceId })
    await refresh()
  })

  const dates = dateHints(findings)
  const places = placeHints(findings)

  return (
    <Card>
      <CardHeader><CardTitle className="text-base"><CalendarDays />When, where, and where your files came from</CardTitle></CardHeader>
      <CardContent className="space-y-4 text-sm">
        <label className="block text-xs">A short name for the incident (for example “Market shooting, Gikomba”)
          <input value={name} onChange={e => setName(e.target.value)} maxLength={100} className="mt-0.5 w-full rounded-lg border px-2 py-1 text-sm" />
        </label>

        <div className="space-y-1">
          <p className="font-medium">When did it happen? <span className="text-red-700">required by OTPLink</span></p>
          <div className="flex flex-wrap gap-2">
            <label className="text-xs">From<input type="date" value={from} onChange={e => setFrom(e.target.value)} className="mt-0.5 block rounded-lg border px-2 py-1 text-sm" /></label>
            <label className="text-xs">To (if it lasted more than a day)<input type="date" value={to} onChange={e => setTo(e.target.value)} className="mt-0.5 block rounded-lg border px-2 py-1 text-sm" /></label>
          </div>
          {dates.length > 0 && (
            <p className="text-xs text-muted-foreground">From your files: {dates.map(d => (
              <button key={d.date} type="button" onClick={() => setFrom(d.date)} className="mr-2 underline">{d.date} ({d.why})</button>
            ))}. A file's date is when it was made or saved, which may not be when it happened.</p>
          )}
        </div>

        <div className="space-y-1">
          <p className="flex items-center gap-1 font-medium"><MapPin className="h-4 w-4 text-brand-teal" />Where did it happen? <span className="text-red-700">required by OTPLink</span></p>
          <input value={place} onChange={e => setPlace(e.target.value)} placeholder="Street, area, town" className="w-full rounded-lg border px-2 py-1 text-sm" aria-label="Place" />
          {places.length > 0 && (
            <p className="text-xs text-muted-foreground">From your files: {places.map(p => (
              <button key={p.text} type="button" onClick={() => setPlace(p.text)} className="mr-2 underline">{p.text} ({p.why})</button>
            ))}</p>
          )}
          <p className="text-xs text-muted-foreground">You can also pin the exact spot on the map in the Review step.</p>
        </div>
        <Button size="sm" onClick={() => void save()} disabled={busy}>Save when and where</Button>

        <div className="space-y-2 border-t pt-3">
          <p className="font-medium">Where did each file come from?</p>
          <p className="text-xs text-muted-foreground">This matters a lot to investigators. If you got a file from someone or from social media, say who or which account, and paste the link if you have it.</p>
          {detail.evidence.map(ev => {
            const existing = sourceOf(ev.id)
            const s = sources[ev.id] ?? { kind: 'self', from: '', link: '' }
            const set = (patch: Partial<typeof s>) => setSources({ ...sources, [ev.id]: { ...s, ...patch } })
            return (
              <div key={ev.id} className="rounded-lg border p-2">
                <p className="font-medium">{ev.original_name}</p>
                {existing ? <p className="text-green-900">{String(existing.value.text)}</p> : (
                  <div className="space-y-1">
                    <label className="mr-3"><input type="radio" checked={s.kind === 'self'} onChange={() => set({ kind: 'self' })} /> I recorded it myself</label>
                    <label><input type="radio" checked={s.kind === 'other'} onChange={() => set({ kind: 'other' })} /> I got it from someone or online</label>
                    {s.kind === 'other' && (
                      <div className="grid gap-1 sm:grid-cols-2">
                        <input value={s.from} onChange={e => set({ from: e.target.value })} placeholder="Who, or which app or account" className="rounded-lg border px-2 py-1" aria-label="Who or which account" />
                        <input value={s.link} onChange={e => set({ link: e.target.value })} placeholder="Link, if you have it" className="rounded-lg border px-2 py-1" aria-label="Link" />
                      </div>
                    )}
                    <Button size="sm" variant="outline" onClick={() => void saveSource(ev.id)} disabled={busy}>Save</Button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
        {error && <p role="alert" className="text-red-700">{error}</p>}
      </CardContent>
    </Card>
  )
}
