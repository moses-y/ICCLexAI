"""Finding kind "name_date": a date read from the file's name.

On 2026-11-06 a case built from WhatsApp files ("WhatsApp Video 2025-06-17 at 22.46.40_...mp4") reached the
package with the incident date "not stated": WhatsApp strips the metadata, and the only date left was in the
name. It is when WhatsApp or the camera app saved the file, not necessarily when the events happened, so it
gets its own kind instead of passing as a capture time.

Revision ID: 0004
Revises: 0003
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

OLD = ("capture_time", "gps", "device", "file_properties", "place", "place_candidate", "description", "visible_text",
       "transcript", "entity", "document_summary", "integrity_flag", "geo_conflict", "stated_fact")
NEW = OLD + ("name_date",)


def _check(kinds):
    return "kind IN (" + ", ".join(f"'{k}'" for k in kinds) + ")"


def upgrade() -> None:
    op.drop_constraint("ck_finding_kind", "finding", type_="check")
    op.create_check_constraint("ck_finding_kind", "finding", _check(NEW))


def downgrade() -> None:
    op.drop_constraint("ck_finding_kind", "finding", type_="check")
    op.create_check_constraint("ck_finding_kind", "finding", _check(OLD))
