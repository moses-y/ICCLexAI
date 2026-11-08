// Typed client for the ICCLexAI case API (apps/backend/icclex). Every case route needs the bearer
// token returned once when the case is created; the server stores only its hash.

export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8002'

export type FindingSource = 'extracted' | 'inferred' | 'stated'
export type FindingStatus = 'proposed' | 'confirmed' | 'edited' | 'rejected'

export interface Finding {
  id: string
  evidence_id: string | null
  kind: string
  value: Record<string, unknown>
  source: FindingSource
  confidence: number | null
  status: FindingStatus
  location: { lat: number; lon: number } | null
  supersedes_id: string | null
}

export interface JobState { agent: string; status: 'queued' | 'running' | 'done' | 'failed'; error: string | null; model: string | null }

export interface EvidenceItem {
  id: string
  original_name: string
  mime: string
  size_bytes: number
  sha256: string
  status: 'received' | 'analysing' | 'analysed' | 'failed'
  jobs: JobState[]
}

export interface CaseDetail {
  id: string
  status: 'draft' | 'analysing' | 'review' | 'package_ready' | 'filed_by_user'
  incident_name: string | null
  incident_location_text: string | null
  incident_location: { lat: number; lon: number } | null
  incident_from: string | null
  incident_to: string | null
  external_processing_consent: boolean
  otp_reference: string | null
  evidence: EvidenceItem[]
  package: { version: number; status: 'current' | 'stale' } | null
}

export interface UploadResult {
  original_name: string
  evidence_id?: string
  error?: string
  code?: number
  unrecognised_type?: boolean
}

export interface CustodyView {
  chain_valid: boolean
  problem: string | null
  events: { at: string; event_type: string; actor_type: string; actor_ref: string; evidence_id: string | null }[]
}

export interface OtplinkFields {
  form_checked_on: string
  caveat: string
  limit_warnings: string[]
  fields: { field: string; value: string | null; note?: string; max_chars?: number; max_bytes?: number }[]
  attachments: { label: string; original_name: string; sha256: string; size_bytes: number }[]
  notes: string[]
}

export interface PackageResult {
  version: number
  manifest_sha256: string
  narrative_model: string | null
  removed_from_draft: { text: string; reason: string }[]
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

export interface Session { caseId: string; token: string }

async function request<T>(s: Session | null, path: string, init: RequestInit = {}, raw = false): Promise<T> {
  const headers = new Headers(init.headers)
  if (s) headers.set('Authorization', `Bearer ${s.token}`)
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
  } catch {
    throw new ApiError(0, `Cannot reach the server at ${API_BASE_URL}. Nothing was sent.`)
  }
  if (!res.ok) {
    let detail = res.statusText
    try { const j = await res.json(); detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail) } catch { /* not JSON */ }
    throw new ApiError(res.status, detail)
  }
  return (raw ? res.blob() : res.json()) as Promise<T>
}

const json = (body: unknown) => JSON.stringify(body)
const c = (s: Session) => `/api/cases/${s.caseId}`

export const api = {
  createCase: (consent: boolean, name?: string) =>
    request<{ case_id: string; token: string }>(null, '/api/cases', { method: 'POST', body: json({ external_processing_consent: consent, incident_name: name ?? null }) }),
  getCase: (s: Session) => request<CaseDetail>(s, c(s)),
  updateCase: (s: Session, patch: Record<string, unknown>) => request<CaseDetail>(s, c(s), { method: 'PATCH', body: json(patch) }),
  upload: (s: Session, files: File[]) => {
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    return request<{ results: UploadResult[] }>(s, `${c(s)}/evidence`, { method: 'POST', body: form })
  },
  evidenceBlob: (s: Session, id: string) => request<Blob>(s, `${c(s)}/evidence/${id}/content`, {}, true),
  findings: (s: Session) => request<{ findings: Finding[] }>(s, `${c(s)}/findings`).then(r => r.findings),
  changeFinding: (s: Session, id: string, action: 'confirm' | 'reject' | 'edit', value?: Record<string, unknown>) =>
    request<Finding>(s, `${c(s)}/findings/${id}`, { method: 'PATCH', body: json({ action, value }) }),
  bulk: (s: Session, ids: string[], action: 'confirm' | 'reject') =>
    request<{ changed: number }>(s, `${c(s)}/findings/bulk`, { method: 'POST', body: json({ ids, action }) }),
  addFact: (s: Session, fact: { text: string; when?: string; where?: string; who?: string; evidence_id?: string }) =>
    request<Finding>(s, `${c(s)}/facts`, { method: 'POST', body: json(fact) }),
  interview: (s: Session, message: string) =>
    request<{ reply: string; proposed_facts: Finding[] }>(s, `${c(s)}/interview`, { method: 'POST', body: json({ message }) }),
  custody: (s: Session) => request<CustodyView>(s, `${c(s)}/custody`),
  buildPackage: (s: Session, consentFilesAsTheyAre: boolean) =>
    request<PackageResult>(s, `${c(s)}/package`, { method: 'POST', body: json({ consent_files_as_they_are: consentFilesAsTheyAre }) }),
  otplinkFields: (s: Session) => request<OtplinkFields>(s, `${c(s)}/package/otplink`, {}),
  downloadPackage: (s: Session) => request<Blob>(s, `${c(s)}/package/download`, {}, true),
  markFiled: (s: Session, otpReference?: string) =>
    request<CaseDetail>(s, `${c(s)}/filed`, { method: 'POST', body: json({ otp_reference: otpReference || null }) }),
}
