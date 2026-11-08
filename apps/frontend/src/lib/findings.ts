import type { Finding, FindingSource } from './api'

export const SOURCE_LABEL: Record<FindingSource, { text: string; hint: string; cls: string }> = {
  extracted: { text: 'From the file', hint: 'Read directly from the file or a map lookup. Not an AI guess.', cls: 'bg-blue-100 text-blue-900' },
  inferred: { text: 'AI suggestion', hint: 'A model suggested this. Check it against the file before confirming.', cls: 'bg-amber-100 text-amber-900' },
  stated: { text: 'Your words', hint: 'Said or written by you.', cls: 'bg-green-100 text-green-900' },
}

export const KIND_LABEL: Record<string, string> = {
  capture_time: 'When it was captured', gps: 'GPS location', device: 'Recording device', file_properties: 'File details',
  place: 'Place at the GPS point', place_candidate: 'Possible place (from what is visible)', description: 'What the file shows',
  visible_text: 'Text visible in the file', transcript: 'Speech in the file', entity: 'Named in the file',
  document_summary: 'What the document says', integrity_flag: 'Something worth checking', geo_conflict: 'Location mismatch',
  stated_fact: 'Your account', name_date: 'Date in the file name',
}

const str = (v: unknown) => (v === null || v === undefined ? '' : String(v))

export function describe(f: Finding): string {
  const v = f.value
  switch (f.kind) {
    case 'name_date': return `${str(v.iso)} · from the name “${str(v.from_name)}”, when an app saved the file, not necessarily when it happened`
    case 'capture_time': return `${str(v.iso)} ${v.tz_known ? '' : '(no time zone recorded)'} · ${str(v.field)}`
    case 'gps': return `${Number(v.lat).toFixed(5)}, ${Number(v.lon).toFixed(5)} · ${str(v.field)}`
    case 'place': return str(v.display_name)
    case 'place_candidate': return `${str(v.place)} — because: ${(v.reasons as string[] | undefined)?.join('; ') ?? ''}`
    case 'description': return str(v.text)
    case 'visible_text': return `“${str(v.text)}”${v.language ? ` (${str(v.language)})` : ''}`
    case 'transcript': return str(v.text)
    case 'document_summary': return str(v.summary)
    case 'device': return Object.entries(v).map(([k, x]) => `${k}: ${str(x)}`).join(', ')
    case 'file_properties': return Object.entries(v).filter(([k, x]) => k !== 'streams' && x !== null).map(([k, x]) => `${k}: ${str(x)}`).join(', ')
    case 'integrity_flag': case 'geo_conflict': return str(v.detail)
    case 'stated_fact': return str(v.text)
    default: return JSON.stringify(v)
  }
}

/** Fields a person can correct: the top-level text values. Everything else is carried over unchanged. */
export const editableKeys = (f: Finding) => Object.keys(f.value).filter(k => typeof f.value[k] === 'string')

export const isOpen = (f: Finding) => f.status === 'proposed'
