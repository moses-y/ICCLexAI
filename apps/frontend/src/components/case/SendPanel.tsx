import { useState } from 'react'
import { api, ApiError, type CaseDetail, type Session } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { CheckCircle2, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import FilingAssistant from './FilingAssistant'

interface Props { session: Session; detail: CaseDetail; refresh: () => Promise<void> }

export default function SendPanel({ session, detail, refresh }: Props) {
  const [ref, setRef] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const filed = detail.status === 'filed_by_user'
  const markFiled = async () => {
    setBusy(true); setError(null)
    try { await api.markFiled(session, ref.trim() || undefined); await refresh() }
    catch (e) { setError(e instanceof ApiError ? e.message : String(e)) } finally { setBusy(false) }
  }
  if (detail.package?.status !== 'current') {
    return <Card><CardContent className="pt-4 text-sm">Prepare your submission first (step 4).</CardContent></Card>
  }
  return (
        <Card>
          <CardHeader><CardTitle className="text-base"><Send />File it on OTPLink</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p><strong>Nothing has been sent to the ICC.</strong> You file the package yourself. Sending it does not open a case: the Prosecutor decides what to do with information received.</p>
            <FilingAssistant session={session} version={detail.package.version} />
            {error && <p role="alert" className="text-red-700">{error}</p>}
            {!filed ? (
              <div className="border-t pt-2">
                <label className="block text-xs">Once you have filed it: any reference OTPLink gave you (optional)
                  <input value={ref} onChange={e => setRef(e.target.value)} className="mt-0.5 w-full rounded-lg border px-2 py-1 text-sm" /></label>
                <Button className="mt-2" onClick={() => void markFiled()} disabled={busy}>I have filed this on OTPLink</Button>
                <p className="mt-1 text-xs text-muted-foreground">This only records what you tell us; we cannot check it.</p>
              </div>
            ) : <p className="flex items-center gap-2 rounded-lg border border-brand-teal/20 bg-brand-teal/5 p-3"><CheckCircle2 className="h-4 w-4 text-brand-teal" />Recorded as filed by you{detail.otp_reference ? `. Reference: ${detail.otp_reference}` : ''}.</p>}
          </CardContent>
        </Card>
  )
}
