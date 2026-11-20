"""Check your case queries against kernel_cafe.db.

    python check.py      check all five cases
    python check.py 3    check just case 3

PASS here means your query is right on the database you can see. The grader also
runs it on a hidden copy with different dates and rows, so a query that hardcodes
a date or an ID can pass here and still fail when graded.
"""

import json
import sys

from detective_utils import CASES, CASES_DIR, CHECK_DATA, QueryError, fingerprint, normalize_columns, read_query, run


def check_case(case, expected):
    """Return (status, message) for one case."""
    try:
        sql = read_query(CASES_DIR / case["file"])
        if sql is None:
            return "TODO", "no query yet"
        columns, rows = run(sql)
    except QueryError as e:
        return "ERROR", str(e)

    if normalize_columns(columns) != case["columns"]:
        return "FAIL", (f"columns should be: {', '.join(case['columns'])}\n"
                        f"columns you have:  {', '.join(columns)}")
    if fingerprint(rows) != expected["fingerprint"]:
        return "FAIL", f"columns look right, but these {len(rows)} rows aren't the full answer yet"
    return "PASS", f"{len(rows)} rows"


def main():
    try:
        check_data = json.loads(CHECK_DATA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("Can't find check_data.json. Run this from the mp-data-detective folder.")
        return 1

    wanted = CASES
    if len(sys.argv) > 1:
        wanted = [c for c in CASES if str(c["id"]) == sys.argv[1]]
        if not wanted:
            print("Pick a case from 1 to 5, like: python check.py 3")
            return 1

    passed = 0
    for case in wanted:
        status, message = check_case(case, check_data[str(case["id"])])
        passed += status == "PASS"
        label = f"Case {case['id']}: {case['title']}"
        indent = "\n" + " " * 36
        print(f"{status:6} {label:28} {message.replace(chr(10), indent)}")

    print(f"\n{passed}/{len(wanted)} passing on kernel_cafe.db.")
    print("Reminder: grading also uses a hidden copy, so don't hardcode dates or IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
