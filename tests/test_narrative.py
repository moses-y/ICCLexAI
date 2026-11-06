import pytest

from icclex import narrative
from icclex.agents import llm
from icclex.agents.base import AgentUnavailable
from icclex.db import session_scope
from icclex.models import Finding, NarrativeClaim

from .test_db_integrity import make_case, make_evidence, make_finding


def setup_case(s):
    c = make_case(s)
    ev = make_evidence(s, c)
    gps = make_finding(s, c, ev, kind="gps", value={"lat": -1.28639, "lon": 36.81722, "field": "EXIF GPS"}, source="extracted",
                       status="confirmed")
    desc = make_finding(s, c, ev, kind="description", value={"text": "a crowd on a road"}, status="confirmed")
    fact = make_finding(s, c, None, kind="stated_fact", value={"text": "I saw the crowd at noon"}, source="stated", status="confirmed")
    unconfirmed = make_finding(s, c, ev, kind="visible_text", value={"text": "SECRET", "language": None})
    return c, gps, desc, fact, unconfirmed


def test_sentences_with_legal_conclusions_or_no_citation_are_dropped_and_reported(monkeypatch):
    with session_scope() as s:
        c, gps, desc, fact, unconfirmed = setup_case(s)

        def fake(system, user, model=None):
            assert "SECRET" not in user  # an unconfirmed finding is never shown to the model
            return {"sentences": [
                {"text": "The file records GPS coordinates near Nairobi.", "cites": ["F1"]},
                {"text": "This is a prima facie war crime and the ICC has clear jurisdiction.", "cites": ["F2"]},
                {"text": "The soldiers committed crimes against humanity.", "cites": ["F2"]},
                {"text": "Everyone knows what happened.", "cites": []},
                {"text": "Citing something that does not exist.", "cites": ["F99"]},
                {"text": "The submitter reports seeing a crowd at noon.", "cites": ["F3"]},
            ]}, "fake-model"

        monkeypatch.setattr(llm, "complete_json", fake)
        result = narrative.build_narrative(s, c.id, use_model=True)

        kept = [cl.text for cl in s.query(NarrativeClaim).filter_by(narrative_id=result.narrative.id)]
        assert kept == ["The file records GPS coordinates near Nairobi.", "The submitter reports seeing a crowd at noon."]
        assert len(result.dropped) == 4
        reasons = " ".join(d["reason"] for d in result.dropped)
        assert "legal conclusion" in reasons and "no citation" in reasons
        assert "prima facie" not in result.narrative.body and "crimes against humanity" not in result.narrative.body


@pytest.mark.parametrize("text", [
    "This is a prima facie case.", "The ICC clearly has jurisdiction.", "The soldiers are guilty.",
    "The attack constitutes a war crime.", "These events amount to genocide.", "Proceed to formal investigation.",
    "They committed a crime against humanity.",
])
def test_legal_conclusions_are_recognised(text):
    assert narrative.LEGAL_CONCLUSION.search(text)


@pytest.mark.parametrize("text", [
    "The video shows people running.", "The submitter reports hearing gunfire.", "The file records GPS coordinates.",
    "A document dated 15 June describes an incident.",
])
def test_ordinary_descriptions_are_not_blocked(text):
    assert not narrative.LEGAL_CONCLUSION.search(text)


def test_without_a_model_the_narrative_is_a_plain_attributed_record():
    with session_scope() as s:
        c, *_ = setup_case(s)
        result = narrative.build_narrative(s, c.id, use_model=False)
        assert result.narrative.model is None and not result.dropped
        body = result.narrative.body
        assert "From the file: GPS coordinates -1.28639, 36.81722" in body
        assert "The submitter states: I saw the crowd at noon." in body
        assert "SECRET" not in body  # unconfirmed


def test_model_outage_falls_back_to_the_record_and_says_so(monkeypatch):
    def down(*a, **k):
        raise AgentUnavailable("GROQ_API_KEY is not set")

    monkeypatch.setattr(llm, "complete_json", down)
    with session_scope() as s:
        c, *_ = setup_case(s)
        result = narrative.build_narrative(s, c.id, use_model=True)
        assert result.narrative.model is None
        assert any("model unavailable" in d["reason"] for d in result.dropped)


def test_nothing_to_write_from_is_an_error():
    with session_scope() as s:
        c = make_case(s)
        make_finding(s, c)  # proposed only
        with pytest.raises(ValueError, match="no confirmed findings"):
            narrative.build_narrative(s, c.id, use_model=False)


def test_a_new_narrative_marks_the_previous_one_stale():
    with session_scope() as s:
        c, *_ = setup_case(s)
        first = narrative.build_narrative(s, c.id, use_model=False).narrative
        second = narrative.build_narrative(s, c.id, use_model=False).narrative
        assert (first.status, second.status, second.version) == ("stale", "draft", 2)
    assert Finding  # imported for type clarity
