import { useState } from 'react'
import { api, ApiError, type CaseDetail, type Finding, type Session } from '@/lib/api'
import { describe, editableKeys, KIND_LABEL, SOURCE_LABEL } from '@/lib/findings'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }

const STATUS_CLS: Record<string, string> = {
  proposed: 'bg-gray-100 text-gray-800', confirmed: 'bg-green-100 text-green-900', edited: 'bg-green-100 text-green-900', rejected: 'bg-red-100 text-red-900',
}

function FindingRow({ session, f, refresh }: { session: Session; f: Finding; refresh: () => Promise<void> }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)
  const src = SOURCE_LABEL[f.source]
  const act = async (action: 'confirm' | 'reject' | 'edit', value?: Record<string, unknown>) => {
    try { setError(null); await api.changeFinding(session, f.id, action, value); setEditing(false); await refresh() }
    catch (e) { setError(e instanceof ApiError ? e.message : String(e)) }
  }
  const startEdit = () => { setDraft(Object.fromEntries(editableKeys(f).map(k => [k, String(f.value[k])]))); setEditing(true) }

  return (
    <li className="space-y-1 border-t py-2 first:border-t-0">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="font-medium">{KIND_LABEL[f.kind] ?? f.kind}</span>
        <span className={`rounded px-1.5 py-0.5 ${src.cls}`} title={src.hint}>{src.text}</span>
        <span className={`rounded px-1.5 py-0.5 ${STATUS_CLS[f.status]}`}>{f.status}</span>
      </div>
      {editing ? (
        <div className="space-y-1">
          {Object.keys(draft).map(k => (
            <label key={k} className="block text-xs">{k}
              <textarea value={draft[k]} onChange={e => setDraft({ ...draft, [k]: e.target.value })} className="mt-0.5 w-full rounded border p-1 text-sm" rows={3} />
            </label>
          ))}
          <Button size="sm" onClick={() => void act('edit', { ...f.value, ...draft })}>Save my wording</Button>{' '}
          <Button size="sm" variant="outline" onClick={() => setEditing(false)}>Cancel</Button>
        </div>
      ) : (
        <p className="whitespace-pre-wrap break-words text-sm">{describe(f)}</p>
      )}
      {f.kind === 'integrity_flag' && <p className="text-xs text-gray-600">A flag is not a finding of tampering; it is something worth checking.</p>}
      {!editing && (
        <div className="flex flex-wrap gap-1">
          {f.status !== 'confirmed' && f.status !== 'edited' && <Button size="sm" onClick={() => void act('confirm')}>Confirm</Button>}
          {editableKeys(f).length > 0 && <Button size="sm" variant="outline" onClick={startEdit}>Edit</Button>}
          {f.status !== 'rejected' && <Button size="sm" variant="outline" onClick={() => void act('reject')}>Reject</Button>}
        </div>
      )}
      {error && <p role="alert" className="text-xs text-red-700">{error}</p>}
    </li>
  )
}

export default function FindingsPanel({ session, detail, findings, refresh }: Props) {
  const [error, setError] = useState<string | null>(null)
  const open = findings.filter(f => f.status === 'proposed')
  const extractedOpen = open.filter(f => f.source === 'extracted')
  const bulkConfirm = async () => {
    try { setError(null); await api.bulk(session, extractedOpen.map(f => f.id), 'confirm'); await refresh() }
    catch (e) { setError(e instanceof ApiError ? e.message : String(e)) }
  }
  const conflicts = findings.filter(f => f.kind === 'geo_conflict' && f.status !== 'rejected')

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="space-y-2 pt-4 text-sm">
          <p>Only what you <strong>confirm</strong> goes into your package. “From the file” items were read directly; “AI suggestion” items are guesses and can be wrong, so check each against the file before confirming. Edit or reject anything that is not right.</p>
          <p>{open.length} still to review.</p>
          {extractedOpen.length > 0 && <Button size="sm" variant="outline" onClick={() => void bulkConfirm()}>Confirm all {extractedOpen.length} items read from the files</Button>}
          {error && <p role="alert" className="text-red-700">{error}</p>}
          {conflicts.map(c => <p key={c.id} className="rounded bg-amber-50 p-2">{describe(c)}</p>)}
        </CardContent>
      </Card>
      {detail.evidence.map(ev => {
        const mine = findings.filter(f => f.evidence_id === ev.id)
        return (
          <Card key={ev.id}>
            <CardHeader><CardTitle className="text-sm">{ev.original_name}</CardTitle></CardHeader>
            <CardContent>
              {mine.length === 0 ? <p className="text-sm text-gray-600">Nothing was found for this file.</p>
                : <ul>{mine.map(f => <FindingRow key={f.id} session={session} f={f} refresh={refresh} />)}</ul>}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
