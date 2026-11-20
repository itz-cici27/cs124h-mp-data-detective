"""Pre-release self-test.  (STAFF ONLY)

    python staff/selftest.py

Checks that:
  1. Each reference solution catches exactly the planted rows, across many seeds.
  2. The owner's AI duplicate check returns 0 rows (the AI question depends on it).
  3. The grader gives the reference solutions 80/80 and the empty starter files 0/80.
  4. Hardcoded answers pass on the public database but fail on the hidden copy.
  5. check.py reports PASS for every reference solution.
"""

import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "staff"))

from detective_utils import CASES, DEFAULT_DB, fingerprint, read_query, run  # noqa: E402
from generate_db import HIDDEN_SEED, PUBLIC_SEED, build  # noqa: E402
import grade  # noqa: E402

AI_QUERY = "SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1"
SOLUTIONS = ROOT / "staff" / "solutions"
failures = []


def check(condition, message):
    if not condition:
        failures.append(message)
        print("  FAIL:", message)


def test_seeds(tmp):
    print("1-2. Reference solutions vs. planted rows, and the AI query")
    seeds = list(range(1, 31)) + [PUBLIC_SEED, HIDDEN_SEED]
    for seed in seeds:
        db = tmp / f"seed{seed}.db"
        truth, info = build(seed, db)
        for case in CASES:
            _, rows = run(read_query(SOLUTIONS / case["file"]), db)
            check(fingerprint(rows) == fingerprint(truth[case["id"]]),
                  f"seed {seed}, case {case['id']}: solution found {len(rows)} rows, planted {len(truth[case['id']])}")
            check(len(rows) > 0, f"seed {seed}, case {case['id']}: no planted rows")
        check(info["counts"][4] >= 20, f"seed {seed}: only {info['counts'][4]} night-owl rows, bump too small")
        check(len(run(AI_QUERY, db)[1]) == 0, f"seed {seed}: the AI duplicate check found rows")

        # The cents week should stand out by roughly 100x in weekly revenue.
        con = sqlite3.connect(db)
        weekly = [r[0] for r in con.execute(
            "SELECT SUM(quantity * unit_price) FROM orders GROUP BY strftime('%W', ordered_at)")]
        con.close()
        weekly.sort()
        check(weekly[-1] / weekly[-2] > 30, f"seed {seed}: the 100x week doesn't stand out")
    print(f"   checked {len(seeds)} seeds")


def test_grader(tmp):
    print("3-4. Grader on solutions, starter files, and hardcoded answers")
    hidden = tmp / "hidden.db"
    truth, info = build(HIDDEN_SEED, hidden)

    scores = {r["case"]: r["points"] for r in grade.grade(SOLUTIONS, hidden)}
    check(sum(scores.values()) == 80, f"reference solutions scored {sum(scores.values())}/80")

    scores = {r["case"]: r["points"] for r in grade.grade(ROOT / "cases", hidden)}
    check(sum(scores.values()) == 0, f"starter files scored {sum(scores.values())}/80 (are cases/ filled in?)")

    # Build hardcoded answers from the public database's answers.
    public_truth, public_info = build(PUBLIC_SEED, tmp / "public_copy.db")
    hard = tmp / "hardcoded"
    hard.mkdir()
    ids = lambda case: ", ".join(str(row[0]) for row in public_truth[case])  # noqa: E731
    start, end = public_info["cents_week"].split(" to ")
    queries = {
        "case2_impossible.sql": f"SELECT order_id, quantity FROM orders WHERE order_id IN ({ids(2)})",
        "case3_prices.sql": (f"SELECT order_id, unit_price FROM orders "
                             f"WHERE DATE(ordered_at) BETWEEN '{start}' AND '{end}'"),
        "case4_night_owls.sql": f"SELECT order_id, register_id, ordered_at FROM orders WHERE order_id IN ({ids(4)})",
        "case5_ghost_items.sql": f"SELECT order_id, item_id FROM orders WHERE item_id = {public_info['ghost_item_id']}",
    }
    for name, sql in queries.items():
        (hard / name).write_text(sql + ";\n", encoding="utf-8")
    shutil.copy(SOLUTIONS / "case1_duplicates.sql", hard / "case1_duplicates.sql")

    for r in grade.grade(hard, hidden):
        if r["case"] == 1:
            continue
        check(r["points"] == 0 and "hidden copy" in r["feedback"],
              f"hardcoded case {r['case']} should pass public and fail hidden: {r['feedback']}")
    print("   done")


def test_check_py(tmp):
    print("5. check.py on the reference solutions")
    copy = tmp / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("staff", ".git", "__pycache__"))
    for case in CASES:
        shutil.copy(SOLUTIONS / case["file"], copy / "cases" / case["file"])
    out = subprocess.run([sys.executable, "check.py"], cwd=copy, capture_output=True, text=True).stdout
    check(out.count("PASS") == 5, "check.py didn't PASS all five solutions:\n" + out)
    data = json.loads((ROOT / "check_data.json").read_text())
    for case in CASES:
        _, rows = run(read_query(SOLUTIONS / case["file"]), DEFAULT_DB)
        check(data[str(case["id"])]["fingerprint"] == fingerprint(rows),
              f"check_data.json is stale for case {case['id']}; rerun staff/generate_db.py")
    print("   done")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        test_seeds(tmp)
        test_grader(tmp)
        test_check_py(tmp)
    print()
    if failures:
        print(f"{len(failures)} problem(s) found.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
