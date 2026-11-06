"""Mermaid ER diagram generated from the SQLAlchemy tables, so the diagram in docs/SYSTEM_DESIGN.md
cannot drift from the schema (tests/test_erd_doc.py compares them).   python -m icclex.erd"""

import re

from . import models  # noqa: F401  (registers the tables)
from .db import Base


def _type(col) -> str:
    return re.sub(r"[^A-Za-z0-9_\-\[\]()]", "_", str(col.type)).strip("_") or "UNKNOWN"


def mermaid() -> str:
    tables = sorted(Base.metadata.tables.values(), key=lambda t: t.name)
    lines = ["erDiagram"]
    for t in tables:
        for col in t.columns:
            for fk in col.foreign_keys:
                parent = "|o" if col.nullable else "||"  # a nullable FK means the parent is optional
                lines.append(f'    {fk.column.table.name.upper()} {parent}--o{{ {t.name.upper()} : "{col.name}"')
    for t in tables:
        lines.append(f"    {t.name.upper()} {{")
        for col in t.columns:
            keys = ",".join(k for k, on in (("PK", col.primary_key), ("FK", bool(col.foreign_keys))) if on)
            lines.append(f"        {_type(col)} {col.name}{' ' + keys if keys else ''}")
        lines.append("    }")
    return "\n".join(lines)


if __name__ == "__main__":
    print(mermaid())
