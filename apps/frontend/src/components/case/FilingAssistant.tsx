import { useEffect, useState } from 'react'
import { api, ApiError, type OtplinkFields, type Session } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Check, Copy, ExternalLink } from 'lucide-react'

const OTPLINK_URL = 'https://otplink.icc-cpi.int'

// The person files on OTPLink themselves: it has no API and its form sits behind a reCAPTCHA. This does every
// step around that: checks their own files against the manifest, opens the form after a confirmation, and gives
// each field in the form's order with a copy button.

async function sha256(file: File): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', await file.arrayBuffer())
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('')
}

function CopyButton({ text }: { text: string }) {
  const [done, setDone] = useState(false)
  const copy = async () => { await navigator.clipboard.writeText(text); setDone(true); setTimeout(() => setDone(false), 1500) }
  return <Button size="sm" variant="outline" onClick={() => void copy()}>{done ? <><Check />Copied</> : <><Copy />Copy</>}</Button>
}

export default function FilingAssistant({ session, version }: { session: Session; version: number }) {
  const [o, setO] = useState<OtplinkFields | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [checked, setChecked] = useState<Record<string, string>>({}) // sha256 -> name of the matching file chosen
  const [unmatched, setUnmatched] = useState<string[]>([])
  const [hashing, setHashing] = useState(false)
  const [safeNetwork, setSafeNetwork] = useState(false)
  const [identityChosen, setIdentityChosen] = useState(false)

  useEffect(() => {
    api.otplinkFields(session).then(setO).catch(e => setError(e instanceof ApiError ? e.message : String(e)))
  }, [session, version])

  const checkFiles = async (files: FileList | null) => {
    if (!files || !o) return
    setHashing(true)
    const wanted = new Set(o.attachments.map(a => a.sha256))
    const found: Record<string, string> = { ...checked }
    const bad: string[] = []
    for (const f of Array.from(files)) {
      const h = await sha256(f)
      if (wanted.has(h)) found[h] = f.name
      else bad.push(f.name)
    }
    setChecked(found); setUnmatched(bad); setHashing(false)
  }

  if (error) return <p role="alert" className="text-red-700">{error}</p>
  if (!o) return <p>Loading…</p>
  const allChecked = o.attachments.every(a => checked[a.sha256])

  return (
    <div className="space-y-4">
      {o.limit_warnings.length > 0 && (
        <div className="rounded bg-amber-50 p-2"><strong>Over OTPLink's limits:</strong>
          <ul className="list-disc pl-5">{o.limit_warnings.map(w => <li key={w}>{w}</li>)}</ul></div>
      )}

      <section className="space-y-1">
        <h3 className="flex items-center gap-2 font-medium text-brand-navy"><span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-brand-navy to-brand-teal text-xs text-white">1</span>Check your files</h3>
        <p>Choose the files on your device. They are checked here in your browser and are <strong>not uploaded</strong>. A match proves each is the same file that was analysed.</p>
        <input type="file" multiple onChange={e => void checkFiles(e.target.files)} aria-label="Choose your files to check" />
        {hashing && <p>Checking…</p>}
        {unmatched.length > 0 && <p className="text-red-700">Not a file in this case (or changed since it was analysed): {unmatched.join(', ')}</p>}
      </section>

      <section className="space-y-1">
        <h3 className="flex items-center gap-2 font-medium text-brand-navy"><span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-brand-navy to-brand-teal text-xs text-white">2</span>Before you open OTPLink</h3>
        <label className="flex gap-2"><input type="checkbox" checked={safeNetwork} onChange={e => setSafeNetwork(e.target.checked)} className="mt-1" />
          <span>I am on a device and network I trust, without a VPN or proxy (OTPLink asks for this). A private browser window is a good idea.</span></label>
        <label className="flex gap-2"><input type="checkbox" checked={identityChosen} onChange={e => setIdentityChosen(e.target.checked)} className="mt-1" />
          <span>I have decided whether to give my name or file anonymously, whichever is safe for me.</span></label>
        {!allChecked && <p className="text-muted-foreground">Not every file has been checked yet. You can still go on.</p>}
        <Button disabled={!safeNetwork || !identityChosen} onClick={() => window.open(OTPLINK_URL, '_blank', 'noopener,noreferrer')}><ExternalLink />Open OTPLink in a new tab</Button>
      </section>

      <section className="space-y-2">
        <h3 className="flex items-center gap-2 font-medium text-brand-navy"><span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-brand-navy to-brand-teal text-xs text-white">3</span>Fill in the form, field by field</h3>
        <p className="text-xs text-muted-foreground">In the order OTPLink shows them, as checked on {o.form_checked_on}. If the live form differs, follow the live form.</p>
        {o.fields.map(f => {
          const len = f.value?.length ?? 0
          const over = (f.max_chars && len > f.max_chars) || (f.max_bytes && new TextEncoder().encode(f.value ?? '').length > f.max_bytes)
          return (
            <div key={f.field} className="rounded-lg border p-2">
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{f.field}</span>
                {f.value && <CopyButton text={f.value} />}
              </div>
              {f.value && <p className="mt-1 max-h-40 overflow-y-auto whitespace-pre-wrap rounded bg-gray-50 p-1.5">{f.value}</p>}
              {f.max_chars && <p className={`text-xs ${over ? 'text-red-700' : 'text-muted-foreground'}`}>{len} of {f.max_chars} characters</p>}
              {f.note && <p className="text-xs text-muted-foreground">{f.note}</p>}
            </div>
          )
        })}
      </section>

      <section className="space-y-1">
        <h3 className="flex items-center gap-2 font-medium text-brand-navy"><span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-brand-navy to-brand-teal text-xs text-white">4</span>Add the attachments, in this order</h3>
        <ol className="space-y-1">
          {o.attachments.map(a => (
            <li key={a.label} className="flex flex-wrap items-center gap-2">
              <span className="font-mono">{a.label}</span>
              <span>{a.original_name}</span>
              {checked[a.sha256]
                ? <span className="rounded-full bg-brand-teal/10 px-2 text-xs text-brand-teal">checked: {checked[a.sha256]}</span>
                  : <span className="rounded bg-gray-100 px-1.5 text-xs text-gray-800">not checked</span>}
            </li>
          ))}
        </ol>
        {o.notes.map(n => <p key={n} className="text-xs text-muted-foreground">{n}</p>)}
      </section>
    </div>
  )
}
