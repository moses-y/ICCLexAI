"""Integrity triggers: the guarantees the design promises, enforced by the database itself.

- evidence: hash, size, path and case are write-once.
- custody_event: no UPDATE, DELETE or TRUNCATE for anyone, the table owner included.
- finding: what a finding says is immutable; only its review status can change. An edit is a new row.
- narrative_claim: it may only cite a confirmed or edited finding.

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE FUNCTION evidence_write_once() RETURNS trigger AS $$
    BEGIN
        IF NEW.sha256 IS DISTINCT FROM OLD.sha256 OR NEW.storage_uri IS DISTINCT FROM OLD.storage_uri
           OR NEW.size_bytes IS DISTINCT FROM OLD.size_bytes OR NEW.case_id IS DISTINCT FROM OLD.case_id THEN
            RAISE EXCEPTION 'evidence hash, size, path and case are write-once (evidence %)', OLD.id;
        END IF;
        RETURN NEW;
    END $$ LANGUAGE plpgsql;
    CREATE TRIGGER evidence_write_once BEFORE UPDATE ON evidence
        FOR EACH ROW EXECUTE FUNCTION evidence_write_once();

    CREATE FUNCTION custody_event_append_only() RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'custody_event is append-only';
    END $$ LANGUAGE plpgsql;
    CREATE TRIGGER custody_event_no_change BEFORE UPDATE OR DELETE ON custody_event
        FOR EACH ROW EXECUTE FUNCTION custody_event_append_only();
    CREATE TRIGGER custody_event_no_truncate BEFORE TRUNCATE ON custody_event
        FOR EACH STATEMENT EXECUTE FUNCTION custody_event_append_only();

    CREATE FUNCTION finding_immutable() RETURNS trigger AS $$
    BEGIN
        IF NEW.value IS DISTINCT FROM OLD.value OR NEW.kind IS DISTINCT FROM OLD.kind
           OR NEW.source IS DISTINCT FROM OLD.source OR NEW.evidence_id IS DISTINCT FROM OLD.evidence_id
           OR NEW.case_id IS DISTINCT FROM OLD.case_id OR NEW.geom IS DISTINCT FROM OLD.geom
           OR NEW.confidence IS DISTINCT FROM OLD.confidence THEN
            RAISE EXCEPTION 'a finding cannot be rewritten; add a new finding that supersedes it (finding %)', OLD.id;
        END IF;
        RETURN NEW;
    END $$ LANGUAGE plpgsql;
    CREATE TRIGGER finding_immutable BEFORE UPDATE ON finding
        FOR EACH ROW EXECUTE FUNCTION finding_immutable();

    CREATE FUNCTION narrative_claim_citable() RETURNS trigger AS $$
    DECLARE s text;
    BEGIN
        SELECT status INTO s FROM finding WHERE id = NEW.finding_id;
        IF s IS NULL OR s NOT IN ('confirmed', 'edited') THEN
            RAISE EXCEPTION 'a narrative claim must cite a confirmed or edited finding (finding % is %)',
                NEW.finding_id, COALESCE(s, 'missing');
        END IF;
        RETURN NEW;
    END $$ LANGUAGE plpgsql;
    CREATE TRIGGER narrative_claim_citable BEFORE INSERT OR UPDATE ON narrative_claim
        FOR EACH ROW EXECUTE FUNCTION narrative_claim_citable();
    """)


def downgrade() -> None:
    op.execute("""
    DROP TRIGGER narrative_claim_citable ON narrative_claim;
    DROP FUNCTION narrative_claim_citable();
    DROP TRIGGER finding_immutable ON finding;
    DROP FUNCTION finding_immutable();
    DROP TRIGGER custody_event_no_truncate ON custody_event;
    DROP TRIGGER custody_event_no_change ON custody_event;
    DROP FUNCTION custody_event_append_only();
    DROP TRIGGER evidence_write_once ON evidence;
    DROP FUNCTION evidence_write_once();
    """)
