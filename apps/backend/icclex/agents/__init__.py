"""Which agents run for which kind of file, and in what order."""

from collections.abc import Callable

from ..sniff import kind_of
from . import audio_video, document, geolocation, integrity, metadata, visual
from .base import AgentContext, AgentResult

REGISTRY: dict[str, Callable[[AgentContext], AgentResult]] = {
    "metadata": metadata.run, "geolocation": geolocation.run, "visual": visual.run,
    "audio_video": audio_video.run, "document": document.run, "integrity": integrity.run,
}

# (agent, agent it must wait for). Geolocation and integrity read the metadata agent's findings.
PLANS: dict[str, list[tuple[str, str | None]]] = {
    "image": [("metadata", None), ("geolocation", "metadata"), ("visual", None), ("integrity", "metadata")],
    "video": [("metadata", None), ("geolocation", "metadata"), ("visual", None), ("audio_video", None),
              ("integrity", "metadata")],
    "audio": [("metadata", None), ("audio_video", None), ("integrity", "metadata")],
    "document": [("metadata", None), ("document", None), ("integrity", "metadata")],
}


def plan_for(mime: str) -> list[tuple[str, str | None]]:
    return PLANS.get(kind_of(mime), [("metadata", None), ("integrity", "metadata")])
