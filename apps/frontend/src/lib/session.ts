import type { Session } from './api'

// The case key lives only in this browser. There is no account and no recovery: the server keeps a
// hash of the token, so a lost key cannot be reissued. Storage can be blocked (private windows), so
// every access is guarded and the app works without it.
const KEY = 'icclexai.case'

export function loadSession(): Session | null {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as Session) : null
  } catch {
    return null
  }
}

export function saveSession(s: Session): boolean {
  try { localStorage.setItem(KEY, JSON.stringify(s)); return true } catch { return false }
}

export function forgetSession(): void {
  try { localStorage.removeItem(KEY) } catch { /* nothing stored */ }
}

export const toKeyString = (s: Session) => `${s.caseId}.${s.token}`

export function parseKeyString(text: string): Session | null {
  const m = text.trim().match(/^([0-9a-f-]{36})\.([\w-]{20,})$/i)
  return m ? { caseId: m[1], token: m[2] } : null
}
