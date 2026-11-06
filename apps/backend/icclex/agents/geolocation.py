"""Where was this? Three separate answers, kept separate and labelled:
- the place GPS in the file points to (reverse geocoded, needs consent: coordinates leave the server),
- place candidates from visible clues (a vision model, inferred, ranked, with reasons, no coordinates),
- a conflict flag when file GPS and the place the submitter stated are far apart (local arithmetic)."""

import math
import threading
import time

from .. import config
from .base import AgentContext, AgentResult, AgentTransient, AgentUnavailable, FindingDraft, require_consent
from .frames import downscaled_jpeg, extract_keyframes
from .llm import vision_json

_geocode_lock = threading.Lock()
_last_call = 0.0
_cache: dict[tuple[float, float], dict] = {}


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def reverse_geocode(lat: float, lon: float) -> dict:
    """Nominatim, at most one request per second, cached by 5-decimal coordinate (about 1 m)."""
    global _last_call
    key = (round(lat, 5), round(lon, 5))
    if key in _cache:
        return _cache[key]
    from geopy.geocoders import Nominatim

    with _geocode_lock:
        wait = config.NOMINATIM_MIN_INTERVAL_S - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        try:
            loc = Nominatim(user_agent=config.NOMINATIM_USER_AGENT, timeout=10).reverse(
                f"{lat}, {lon}", language="en", zoom=18)
        except Exception as exc:
            raise AgentUnavailable(f"reverse geocoding failed: {exc}") from exc
        finally:
            _last_call = time.monotonic()
    if loc is None:
        raise AgentUnavailable("reverse geocoding found no place at these coordinates")
    addr = loc.raw.get("address", {})
    _cache[key] = {"display_name": loc.address, "country": addr.get("country"), "state": addr.get("state"),
                   "county": addr.get("county"), "city": addr.get("city") or addr.get("town") or addr.get("village"),
                   "via": "nominatim"}
    return _cache[key]


CLUE_SYSTEM = (
    "You help a human document where a photo or video was taken. Use only what is visible: signs and "
    "their language, landmarks, buildings, vegetation, terrain, vehicles, road markings. Never identify "
    "people. Never invent coordinates. If there is not enough to say, return an empty list. Reply with "
    'JSON: {"candidates": [{"place": str, "reasons": [str]}], "uncertainties": [str]} with at most 3 '
    "candidates, best first. Each reason must name something actually visible."
)


def _images_for(ctx: AgentContext) -> list[tuple[bytes, str]]:
    if ctx.mime.startswith("image/"):
        return [(downscaled_jpeg(ctx.path), "image/jpeg")]
    if ctx.mime.startswith("video/"):
        return [(jpg, "image/jpeg") for _, jpg in extract_keyframes(ctx.path, config.VISION_MAX_IMAGES)]
    return []


def run(ctx: AgentContext) -> AgentResult:
    out: list[FindingDraft] = []
    notes: list[str] = []
    gps = [f for f in ctx.prior_findings if f["kind"] == "gps"]

    if gps:
        lat, lon = gps[0]["value"]["lat"], gps[0]["value"]["lon"]
        if ctx.case_location is not None:
            km = haversine_km((lat, lon), ctx.case_location)
            if km > config.GPS_CONFLICT_KM:
                out.append(FindingDraft("geo_conflict", {
                    "file_gps": {"lat": lat, "lon": lon}, "stated_location": {
                        "lat": ctx.case_location[0], "lon": ctx.case_location[1]},
                    "distance_km": round(km, 1),
                    "detail": f"GPS in the file is {km:.0f} km from the place you said this happened. "
                              "Check which is right; both may be, if the file was taken somewhere else."},
                    "extracted", geom=(lat, lon)))
        try:
            require_consent(ctx)
            place = reverse_geocode(lat, lon)
            out.append(FindingDraft("place", place, "extracted", geom=(lat, lon)))
        except AgentTransient:
            raise  # retry the whole job later rather than record "not analysed"
        except AgentUnavailable as exc:
            notes.append(f"place name for the GPS point not looked up: {exc}")

    images = _images_for(ctx)
    if images:
        try:
            require_consent(ctx)
            data, model = vision_json(CLUE_SYSTEM, "Which places do the visible clues suggest?", images)
            for rank, cand in enumerate(data.get("candidates", [])[:3], start=1):
                if cand.get("place") and cand.get("reasons"):
                    out.append(FindingDraft("place_candidate", {
                        "place": str(cand["place"]), "reasons": [str(r) for r in cand["reasons"]], "rank": rank,
                        "uncertainties": data.get("uncertainties", [])}, "inferred"))
            return AgentResult(findings=out, model=model, notes=notes)
        except AgentUnavailable as exc:
            notes.append(f"location clues not analysed: {exc}")
    elif not gps:
        notes.append("no GPS in the file and nothing visual to read clues from")
    return AgentResult(findings=out, notes=notes)
