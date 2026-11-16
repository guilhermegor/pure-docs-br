"""Run every Python fence in the README and docs, and check the ``# <literal>`` results."""

import ast
from pathlib import Path
import re

import pytest


PATH_ROOT = Path(__file__).resolve().parents[2]
LIST_DOCS = ["README.md", "docs/usage.md", "docs/examples.md", "docs/api/reference.md"]
RE_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)
RE_EXPECT = re.compile(r'^(\w+\(.*\))\s+# ("[^"]*"|True|False)(?:,|$)')


def _list_blocks() -> list[tuple[str, str]]:
    return [
        (f"{str_doc}#{int_idx}", str_block)
        for str_doc in LIST_DOCS
        for int_idx, str_block in enumerate(
            RE_FENCE.findall((PATH_ROOT / str_doc).read_text(encoding="utf-8"))
        )
    ]


def _list_mismatches(
    str_block: str,
) -> list[str]:  # complexity-ok: scans doc lines for expectations
    dict_ns: dict[str, object] = {}
    exec(str_block, dict_ns)  # noqa: S102
    list_bad = []
    for str_line in str_block.splitlines():
        cls_match = RE_EXPECT.match(str_line)
        if cls_match is None:
            continue
        obj_got = eval(cls_match.group(1), dict_ns)  # noqa: S307
        if obj_got != ast.literal_eval(cls_match.group(2)):
            list_bad.append(str_line)
    return list_bad


@pytest.mark.parametrize(("str_id", "str_block"), _list_blocks())
def test_doc_python_block_runs_and_matches_comments(str_id: str, str_block: str) -> None:
    """The block executes, and each ``call()  # literal`` line evaluates to that literal."""
    assert _list_mismatches(str_block) == [], str_id
