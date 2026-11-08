import { useState } from 'react'
import { api, ApiError, type CaseDetail, type Finding, type Session } from '@/lib/api'
import { describe } from '@/lib/findings'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MessageSquare, PenSquare, ListChecks } from 'lucide-react'
import IncidentBasics from './IncidentBasics'

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }
interface Turn { role: 'you' | 'assistant'; text: string }

export default function StatementsPanel({ session, detail, findings, refresh }: Props) {
  const [turns, setTurns] = useState<Turn[]>([])
  const [message, setMessage] = useState('')
  const [fact, setFact] = useState({ text: '', when: '', where: '', who: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const statements = findings.filter(f => f.kind === 'stated_fact' && !f.evidence_id)

  const wrap = async (fn: () => Promise<void>) => {
    setBusy(true); setError(null)
    try { await fn() } catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  const send = () => wrap(async () => {
    const text = message.trim(); if (!text) return
    setTurns(t => [...t, { role: 'you', text }]); setMessage('')
    const r = await api.interview(session, text)
    setTurns(t => [...t, { role: 'assistant', text: r.reply }])
    await refresh()
  })
  const addFact = () => wrap(async () => {
    if (!fact.text.trim()) return
    await api.addFact(session, { text: fact.text.trim(), when: fact.when || undefined, where: fact.where || undefined, who: fact.who || undefined })
    setFact({ text: '', when: '', where: '', who: '' }); await refresh()
  })

  return (
    <div className="space-y-4">
      <IncidentBasics session={session} detail={detail} findings={findings} refresh={refresh} />

      <Card>
        <CardHeader><CardTitle className="text-base"><MessageSquare />Tell us what happened</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>Say as much or as little as you want. You can skip anything. Do not include your own name or contact details here. This does not decide whether a crime happened or whether the ICC will act.</p>
          {detail.external_processing_consent ? (
            <>
              <ul className="space-y-2" aria-live="polite">
                {turns.map((t, i) => <li key={i} className={`rounded p-2 ${t.role === 'you' ? 'ml-8 bg-brand-navy/5' : 'mr-8 bg-brand-teal/5'}`}><strong>{t.role === 'you' ? 'You' : 'Assistant'}:</strong> <span className="whitespace-pre-wrap">{t.text}</span></li>)}
              </ul>
              <textarea value={message} onChange={e => setMessage(e.target.value)} rows={3} className="w-full rounded-lg border p-2" placeholder="Write here, in any language" aria-label="Your message" />
              <Button onClick={() => void send()} disabled={busy || !message.trim()}>{busy ? 'Sending…' : 'Send'}</Button>
              <p className="text-xs text-muted-foreground">What you write here is sent to an AI provider to ask follow-up questions and pick out facts. You will confirm each fact below before it is used.</p>
            </>
          ) : (
            <p className="rounded bg-amber-50 p-2">The assistant is off because outside processing is not allowed for this case. You can still write your statements yourself below, or allow outside processing on the Files step.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base"><PenSquare />Write a statement yourself</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <textarea value={fact.text} onChange={e => setFact({ ...fact, text: e.target.value })} rows={3} className="w-full rounded-lg border p-2" placeholder="What you saw, recorded or were told" aria-label="Statement" />
          <div className="grid gap-2 sm:grid-cols-3">
            <label className="text-xs">When (date, YYYY-MM-DD)<input value={fact.when} onChange={e => setFact({ ...fact, when: e.target.value })} className="mt-0.5 w-full rounded-lg border px-2 py-1 text-sm" placeholder="2025-06-15" /></label>
            <label className="text-xs">Where<input value={fact.where} onChange={e => setFact({ ...fact, where: e.target.value })} className="mt-0.5 w-full rounded-lg border px-2 py-1 text-sm" /></label>
            <label className="text-xs">Who (role or description)<input value={fact.who} onChange={e => setFact({ ...fact, who: e.target.value })} className="mt-0.5 w-full rounded-lg border px-2 py-1 text-sm" /></label>
          </div>
          <Button size="sm" onClick={() => void addFact()} disabled={busy || !fact.text.trim()}>Add statement</Button>
          {error && <p role="alert" className="text-red-700">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base"><ListChecks />Your account so far</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          {statements.length === 0 && <p className="text-muted-foreground">Nothing yet.</p>}
          {statements.map(s => (
            <div key={s.id} className="flex flex-wrap items-start justify-between gap-2 border-t pt-2 first:border-t-0">
              <div><p className="whitespace-pre-wrap">{describe(s)}</p><p className="text-xs text-muted-foreground">{[s.value.when, s.value.where, s.value.who].filter(Boolean).join(' · ')} · {s.status}</p></div>
              <div className="flex gap-1">
                {s.status === 'proposed' && <Button size="sm" onClick={() => void api.changeFinding(session, s.id, 'confirm').then(refresh)}>Confirm</Button>}
                {s.status !== 'rejected' && <Button size="sm" variant="outline" onClick={() => void api.changeFinding(session, s.id, 'reject').then(refresh)}>Remove</Button>}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
