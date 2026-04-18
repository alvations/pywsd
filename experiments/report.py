"""Aggregate evaluate.py JSONL into a method × config markdown table.

Usage::

    python experiments/report.py \\
        --files experiments/results_lesk.jsonl \\
                experiments/results_maxsim.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(files: list[Path]) -> list[dict]:
    out: list[dict] = []
    for f in files:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def build_table(rows: list[dict]) -> str:
    # method × config grid
    configs = sorted({r["config"] for r in rows})
    methods: list[str] = []
    seen: set[str] = set()
    for r in rows:
        if r["method"] not in seen:
            methods.append(r["method"])
            seen.add(r["method"])

    acc: dict[tuple[str, str], float] = {}
    totals: dict[tuple[str, str], int] = {}
    for r in rows:
        acc[(r["method"], r["config"])] = r["accuracy"]
        totals[(r["method"], r["config"])] = r["total"]

    # Header
    lines = []
    header = "| method | " + " | ".join(configs) + " |"
    sep = "|--------|" + "|".join(["-" * 18] * len(configs)) + "|"
    lines.append(header)
    lines.append(sep)

    for m in methods:
        cells = []
        for c in configs:
            if (m, c) in acc:
                cells.append(f"{acc[(m, c)]*100:5.2f}% ({totals[(m, c)]})")
            else:
                cells.append("—")
        lines.append(f"| {m} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", nargs="+", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    rows = load(args.files)
    table = build_table(rows)
    print(table)
    if args.out:
        args.out.write_text(table + "\n")
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
