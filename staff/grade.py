"""Autograder for the case queries.  (STAFF ONLY)

    python staff/grade.py                     grade the queries in cases/
    python staff/grade.py path/to/cases       grade another student's folder
    python staff/grade.py path/to/cases --json   print a JSON result for PrairieLearn

Each case is worth 16 points (80 total). A case earns credit only if it returns
the right columns AND the same rows as the reference solution on BOTH the
public database and the hidden check copy, ignoring row order.
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "staff"))

from detective_utils import CASES, DEFAULT_DB, QueryError, fingerprint, normalize_columns, read_query, run  # noqa: E402
from generate_db import HIDDEN_SEED, build  # noqa: E402

POINTS_PER_CASE = 16
SOLUTIONS = ROOT / "staff" / "solutions"


def result_on(sql, db, expected_rows):
    """Return (ok, message) for one query on one database."""
    try:
        columns, rows = run(sql, db)
    except QueryError as e:
        return False, str(e)
    return fingerprint(rows) == fingerprint(expected_rows), f"{len(rows)} rows (expected {len(expected_rows)})"


def grade(cases_dir, hidden_db):
    results = []
    for case in CASES:
        entry = {"case": case["id"], "title": case["title"], "points": 0, "max_points": POINTS_PER_CASE}
        try:
            sql = read_query(Path(cases_dir) / case["file"])
            if sql is None:
                entry["feedback"] = "No query submitted."
                results.append(entry)
                continue
            columns, _ = run(sql, DEFAULT_DB)
        except QueryError as e:
            entry["feedback"] = str(e)
            results.append(entry)
            continue

        if normalize_columns(columns) != case["columns"]:
            entry["feedback"] = f"Columns should be {', '.join(case['columns'])}; got {', '.join(columns)}."
            results.append(entry)
            continue

        reference = read_query(SOLUTIONS / case["file"])
        public_ok, public_msg = result_on(sql, DEFAULT_DB, run(reference, DEFAULT_DB)[1])
        hidden_ok, hidden_msg = result_on(sql, hidden_db, run(reference, hidden_db)[1])

        if public_ok and hidden_ok:
            entry["points"] = POINTS_PER_CASE
            entry["feedback"] = "Correct on both databases."
        elif public_ok:
            entry["feedback"] = ("Correct on the workspace database but not on the hidden copy "
                                 f"({hidden_msg}). This usually means a hardcoded date or ID.")
        else:
            entry["feedback"] = f"Incorrect on the workspace database ({public_msg})."
        results.append(entry)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases_dir", nargs="?", default=ROOT / "cases")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        hidden_db = Path(tmp) / "hidden.db"
        build(HIDDEN_SEED, hidden_db)
        results = grade(args.cases_dir, hidden_db)

    total = sum(r["points"] for r in results)
    if args.json:
        print(json.dumps({"score": total, "max_score": POINTS_PER_CASE * len(CASES), "cases": results}, indent=2))
    else:
        for r in results:
            print(f"Case {r['case']} {r['title']:20} {r['points']:2}/{r['max_points']}  {r['feedback']}")
        print(f"\nTotal: {total}/{POINTS_PER_CASE * len(CASES)}")


if __name__ == "__main__":
    main()
