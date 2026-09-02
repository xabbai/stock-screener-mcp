"""Documentation drift guards: README and docs/field-reference.md must agree with the code."""

import json
import re
import sys
from pathlib import Path

from tv_mcp.field_registry import FIELD_CATEGORIES, get_all_fields
from tv_mcp.tv_mcp import ALLOWED_OPERATIONS

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text()
ALL_FIELDS = get_all_fields()


def _json_blocks(text):
    return re.findall(r"```json\n(.*?)```", text, re.S)


def _backticked(text):
    return re.findall(r"`([^`\n]+)`", text)


def test_field_reference_in_sync():
    sys.path.insert(0, str(ROOT / "scripts"))
    import gen_field_reference  # noqa: E402

    assert (ROOT / "docs" / "field-reference.md").read_text() == gen_field_reference.render(), (
        "docs/field-reference.md is stale; run: python scripts/gen_field_reference.py"
    )


def test_field_reference_lists_every_field():
    doc = (ROOT / "docs" / "field-reference.md").read_text()
    listed = set(re.findall(r"^\| `([^`]+)` \|", doc, re.M))
    assert listed == ALL_FIELDS


def test_readme_json_blocks_parse():
    blocks = _json_blocks(README)
    assert blocks, "README should contain JSON examples"
    for block in blocks:
        json.loads(block)


def test_readme_counts_match_registry():
    assert f"{len(ALL_FIELDS)} TradingView fields" in README
    assert f"{len(ALL_FIELDS)} fields, {len(FIELD_CATEGORIES)} categories" in README


def test_readme_backticked_fields_exist():
    """Any backticked token that is a registry field modulo case must be the exact field name."""
    lower_map = {f.lower(): f for f in ALL_FIELDS}
    bad = sorted({t for t in _backticked(README) if t.lower() in lower_map and t not in ALL_FIELDS})
    assert not bad, f"README uses non-canonical field names: {bad}"


def test_readme_category_table_fields_exist():
    section = README.split("## Field reference", 1)[1].split("## Live data", 1)[0]
    table_rows = [line for line in section.splitlines() if line.startswith("| ") and "Examples" not in line]
    names = {t for line in table_rows for t in _backticked(line)}
    unknown = sorted(n for n in names if n not in ALL_FIELDS)
    assert not unknown, f"Unknown fields in README field reference section: {unknown}"


def test_readme_operators_are_allowed():
    section = README.split("Operators:", 1)[1].split("\n", 1)[0]
    ops = set(_backticked(section))
    assert ops == ALLOWED_OPERATIONS


def test_readme_tool_call_examples_use_valid_fields_and_ops():
    def walk(node):
        if isinstance(node, dict):
            if "left" in node and "op" in node:
                assert node["left"] in ALL_FIELDS, node
                assert node["op"] in ALLOWED_OPERATIONS, node
                if isinstance(node.get("right"), str):
                    assert node["right"] in ALL_FIELDS, node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for block in _json_blocks(README):
        data = json.loads(block)
        walk(data)
        if isinstance(data, dict) and "columns" in data and "filters" in data:
            assert set(data["columns"]) <= ALL_FIELDS
            assert data["sort_by"] in ALL_FIELDS or data["sort_by"] == ""


def test_docstring_field_lists_match_registry():
    from tv_mcp.tv_mcp import screen_stocks

    doc = screen_stocks.__doc__
    section = doc.split("Field categories", 1)[1].split("markets:", 1)[0]
    names = set()
    for line in section.splitlines():
        if ":" in line:
            names |= {n.strip() for n in line.split(":", 1)[1].split(",") if n.strip()}
    assert names == ALL_FIELDS, f"docstring vs registry: missing={ALL_FIELDS - names} extra={names - ALL_FIELDS}"


def test_readme_relative_links_resolve():
    """Every relative link/image target in README must exist (demo asset is produced in Phase 13)."""
    pending = {"docs/assets/demo.gif", "docs/demo-script.md"}  # created by Phase 13 (demo)
    targets = re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", README)
    missing = sorted(
        t
        for t in set(targets)
        if not t.startswith(("http://", "https://")) and t not in pending and not (ROOT / t).exists()
    )
    assert not missing, f"README links to missing files: {missing}"
