import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api, ApiError, type CaseDetail, type Finding, type Session } from '@/lib/api'
import { describe } from '@/lib/findings'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPin } from 'lucide-react'

interface Props { session: Session; detail: CaseDetail; findings: Finding[]; refresh: () => Promise<void> }
const TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

export default function MapPanel({ session, detail, findings, refresh }: Props) {
  const el = useRef<HTMLDivElement>(null)
  const map = useRef<L.Map | null>(null)
  const layer = useRef<L.LayerGroup | null>(null)
  const tiles = useRef<L.TileLayer | null>(null)
  const [useTiles, setUseTiles] = useState(false)
  const [pin, setPin] = useState<{ lat: number; lon: number } | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!el.current || map.current) return
    map.current = L.map(el.current, { worldCopyJump: true }).setView([0, 20], 2)
    layer.current = L.layerGroup().addTo(map.current)
    map.current.on('click', e => setPin({ lat: e.latlng.lat, lon: e.latlng.lng }))
    return () => { map.current?.remove(); map.current = null }
  }, [])

  // Tiles are loaded from openstreetmap.org, which tells that server what area you are looking at.
  // Off by default; without them the points are plotted on a plain background.
  useEffect(() => {
    if (!map.current) return
    if (useTiles && !tiles.current) tiles.current = L.tileLayer(TILES, { maxZoom: 19, attribution: '© OpenStreetMap contributors' }).addTo(map.current)
    if (!useTiles && tiles.current) { tiles.current.remove(); tiles.current = null }
  }, [useTiles])

  const points = findings.filter(f => f.kind === 'gps' && f.location && f.status !== 'rejected')
  useEffect(() => {
    if (!map.current || !layer.current) return
    layer.current.clearLayers()
    const bounds: L.LatLngExpression[] = []
    const name = (f: Finding) => detail.evidence.find(e => e.id === f.evidence_id)?.original_name ?? 'file'
    points.forEach(f => {
      const ll: L.LatLngExpression = [f.location!.lat, f.location!.lon]
      bounds.push(ll)
      L.circleMarker(ll, { radius: 8, color: '#1d4ed8' }).bindPopup(`${name(f)}<br>${describe(f)}<br>${f.status}`).addTo(layer.current!)
    })
    if (detail.incident_location) {
      const ll: L.LatLngExpression = [detail.incident_location.lat, detail.incident_location.lon]
      bounds.push(ll)
      L.circleMarker(ll, { radius: 8, color: '#15803d', fill: true, fillOpacity: 0.6 }).bindPopup('Where you say it happened').addTo(layer.current)
    }
    if (pin) L.circleMarker([pin.lat, pin.lon], { radius: 6, color: '#b45309' }).bindPopup('Pin (not saved yet)').addTo(layer.current)
    if (bounds.length) map.current.fitBounds(L.latLngBounds(bounds).pad(0.3), { maxZoom: 14 })
  }, [points.length, detail.incident_location?.lat, detail.incident_location?.lon, pin?.lat, pin?.lon, detail.evidence, findings]) // eslint-disable-line react-hooks/exhaustive-deps

  const savePin = async () => {
    if (!pin) return
    try { setError(null); await api.updateCase(session, { incident_lat: pin.lat, incident_lon: pin.lon }); setPin(null); await refresh() }
    catch (e) { setError(e instanceof ApiError ? e.message : String(e)) }
  }

  return (
    <Card>
      <CardHeader><CardTitle className="text-base"><MapPin />Where</CardTitle></CardHeader>
      <CardContent className="space-y-2 text-sm">
        <p>Blue: GPS recorded in your files. Green: where you say it happened. Click the map to pin a place; files with no GPS can be tied to the incident this way.</p>
        <div ref={el} className="h-72 w-full rounded border bg-gray-50" role="application" aria-label="Map of file locations" />
        <label className="flex items-center gap-2"><input type="checkbox" checked={useTiles} onChange={e => setUseTiles(e.target.checked)} /> Show street map (loads tiles from openstreetmap.org, which can see the area you view)</label>
        {pin && <div className="flex flex-wrap items-center gap-2"><span>Pin: {pin.lat.toFixed(5)}, {pin.lon.toFixed(5)}</span><Button size="sm" onClick={() => void savePin()}>Use as where it happened</Button><Button size="sm" variant="outline" onClick={() => setPin(null)}>Clear</Button></div>}
        {error && <p role="alert" className="text-red-700">{error}</p>}
        {points.length === 0 && !detail.incident_location && <p className="text-muted-foreground">No file has GPS yet.</p>}
      </CardContent>
    </Card>
  )
}
