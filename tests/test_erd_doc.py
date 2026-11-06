import re
from pathlib import Path

from icclex.erd import mermaid

DOC = Path(__file__).resolve().parents[1] / "docs" / "SYSTEM_DESIGN.md"


def test_the_er_diagram_in_the_design_doc_matches_the_schema():
    text = DOC.read_text()
    block = re.search(r"<!-- erd:start -->\n```mermaid\n(.*?)\n```\n<!-- erd:end -->", text, re.S)
    assert block, "docs/SYSTEM_DESIGN.md has no generated ER block"
    assert block.group(1) == mermaid(), "the schema changed: regenerate the block with `python -m icclex.erd`"
