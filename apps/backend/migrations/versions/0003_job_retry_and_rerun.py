"""Retry a job later after a network error or rate limit, and let the submitter re-run a failed one.

On 2026-11-06 the network dropped during an end-to-end run and two video jobs failed for good with
"Connection error": a transient fault was handled like a missing key, and nothing could re-run them.

- analysis_job.not_before: a retried job is not claimed before this time.
- custody event "reanalysis_requested": a re-run is recorded in the chain like any other action.

Revision ID: 0003
Revises: 0002
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

OLD_EVENTS = ("case_created", "received", "hash_verified", "hash_mismatch", "analysed", "analysis_failed",
              "finding_changed", "exported", "package_built", "filed")
NEW_EVENTS = OLD_EVENTS + ("reanalysis_requested",)


def _events_check(events):
    return "event_type IN (" + ", ".join(f"'{e}'" for e in events) + ")"


def upgrade() -> None:
    op.add_column("analysis_job", sa.Column("not_before", sa.DateTime(timezone=True)))
    op.drop_constraint("ck_custody_event_type", "custody_event", type_="check")
    op.create_check_constraint("ck_custody_event_type", "custody_event", _events_check(NEW_EVENTS))


def downgrade() -> None:
    op.drop_constraint("ck_custody_event_type", "custody_event", type_="check")
    op.create_check_constraint("ck_custody_event_type", "custody_event", _events_check(OLD_EVENTS))
    op.drop_column("analysis_job", "not_before")
