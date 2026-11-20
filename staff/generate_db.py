"""Build the Kernel Café database with five planted data problems.  (STAFF ONLY)

    python staff/generate_db.py                # rebuild kernel_cafe.db and check_data.json
    python staff/generate_db.py --seed 7 --out /tmp/test.db

The same seed always produces the same database. PUBLIC_SEED builds the copy
students work with. HIDDEN_SEED builds the check copy the grader uses: same five
problem types, different dates, rows, and counts, so hardcoded answers fail.

Planted problems (each planted row has exactly one problem):
  1. Duplicates      a register double-tap saves ~40 orders twice (new order_id)
  2. Impossible qty  ~25 rows with quantity 0, negative, or above 10
  3. Cents week      one Monday-Sunday week saved unit_price in cents
  4. Timezone bug    register 2 logged UTC instead of Central for 4 days
  5. Ghost item      ~30 orders for a seasonal item that was removed from the menu
"""

import argparse
import random
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PUBLIC_SEED = 124
HIDDEN_SEED = 6022  # keep this out of the student repo in a real offering

SEMESTER_START = date(2027, 8, 23)  # a Monday; change to match the semester
WEEKS = 17

MENU = [
    # item_id, name, category, price
    (1, "Java Chip Latte", "coffee", 5.25),
    (2, "Kotlin Cold Brew", "coffee", 4.75),
    (3, "Recursive Roast", "coffee", 2.95),
    (4, "Big-O Americano", "coffee", 3.50),
    (5, "Hash Table Chai", "tea", 4.50),
    (6, "Matcha Merge Sort", "tea", 5.50),
    (7, "Null Pointer Bagel", "food", 3.25),
    (8, "Stack Overflow Muffin", "food", 3.75),
    (9, "Binary Breakfast Burrito", "food", 7.95),
    (10, "Boolean Brownie", "food", 2.75),
]
ITEM_WEIGHTS = [16, 13, 14, 11, 9, 8, 9, 8, 7, 5]
PRICES = {item_id: price for item_id, _, _, price in MENU}

GHOST_NAME, GHOST_PRICE = "Pumpkin Spice Pointer", 5.75
GHOST_LAST_DAY = 41  # sold during the first six weeks, then removed

# Open 7 AM to 10 PM. Weight per hour from 7 to 21 (morning rush 8 to 10 AM).
HOURS = list(range(7, 22))
HOUR_WEIGHTS = [3, 9, 10, 8, 6, 7, 6, 5, 5, 4, 4, 3, 3, 2, 2]

QTY_VALUES, QTY_WEIGHTS = [1, 2, 3, 4], [78, 16, 5, 1]
BAD_QUANTITIES = [0, -1, -2, -3, 11, 12, 15, 20, 24, 30]

# Day offsets from SEMESTER_START for the calendar shape.
THANKSGIVING_BREAK = range(89, 98)   # Sat Nov 20 to Sun Nov 28, 2027
FINALS_WEEK = range(109, 117)        # Fri Dec 10 to Fri Dec 17, 2027


def central_utc_offset(d):
    """Hours to add to US Central time to get UTC on day d (5 in daylight time, 6 otherwise)."""
    march = date(d.year, 3, 1)
    dst_start = march + timedelta(days=(6 - march.weekday()) % 7 + 7)  # second Sunday of March
    nov = date(d.year, 11, 1)
    dst_end = nov + timedelta(days=(6 - nov.weekday()) % 7)  # first Sunday of November
    return 5 if dst_start <= d < dst_end else 6


def orders_for_day(rng, offset, d):
    base = 250 if d.weekday() < 5 else 130
    if offset in THANKSGIVING_BREAK:
        base *= 0.25
    if offset in FINALS_WEEK:
        base *= 1.4
    return max(10, int(rng.gauss(base, base * 0.08)))


def build(seed, out_path):
    """Write a database to out_path and return the ground truth for every case."""
    rng = random.Random(seed)
    days = [SEMESTER_START + timedelta(days=i) for i in range(WEEKS * 7)]

    # Where the planted problems go. They never overlap.
    cents_week = rng.randint(2, 10)
    cents_days = set(range(cents_week * 7, cents_week * 7 + 7))
    tz_candidates = [
        s for s in range(7, 61)
        if all(abs((s + k) - c) > 2 for k in range(4) for c in cents_days)
        and all(central_utc_offset(days[s + k]) == central_utc_offset(days[s]) for k in range(5))
    ]
    tz_start = rng.choice(tz_candidates)
    tz_days = set(range(tz_start, tz_start + 4))
    ghost_id = rng.randint(11, 15)

    used_stamps = set()
    rows = []

    def new_row(day_index, register, item_id, qty, shift_hours=0):
        """Pick an unused timestamp during opening hours and build a row."""
        d = days[day_index]
        while True:
            hour = rng.choices(HOURS, HOUR_WEIGHTS)[0]
            true_dt = datetime(d.year, d.month, d.day, hour, rng.randint(0, 59), rng.randint(0, 59))
            stored_dt = true_dt + timedelta(hours=shift_hours)
            if stored_dt not in used_stamps:
                used_stamps.add(stored_dt)
                break
        price = GHOST_PRICE if item_id == ghost_id else PRICES[item_id]
        return {"day": day_index, "true_dt": true_dt, "stored_dt": stored_dt, "register": register,
                "item": item_id, "qty": qty, "price": price, "tags": set(), "copy": False}

    # Normal sales.
    for i, d in enumerate(days):
        for _ in range(orders_for_day(rng, i, d)):
            register = rng.choice([1, 2])
            shift = central_utc_offset(d) if (i in tz_days and register == 2) else 0
            row = new_row(i, register, rng.choices(range(1, 11), ITEM_WEIGHTS)[0],
                          rng.choices(QTY_VALUES, QTY_WEIGHTS)[0], shift)
            if shift:
                row["tags"].add("tz")
            rows.append(row)

    # 5. Ghost item orders during the first six weeks.
    ghost_days = [i for i in range(GHOST_LAST_DAY + 1) if i not in cents_days and i not in tz_days]
    for _ in range(rng.randint(25, 35)):
        row = new_row(rng.choice(ghost_days), rng.choice([1, 2]), ghost_id,
                      rng.choices(QTY_VALUES, QTY_WEIGHTS)[0])
        row["tags"].add("ghost")
        rows.append(row)

    # 3. Cents week: every row that week saved its price in cents.
    for row in rows:
        if row["day"] in cents_days:
            row["price"] = float(round(row["price"] * 100))
            row["tags"].add("cents")

    # 1 and 2 come from clean rows only, away from the timezone days.
    clean = [r for r in rows if not r["tags"] and r["day"] not in tz_days]
    n_dupes, n_impossible = rng.randint(35, 45), rng.randint(20, 30)
    picks = rng.sample(clean, n_dupes + n_impossible)
    dupes, impossible = picks[:n_dupes], picks[n_dupes:]

    for row in impossible:
        row["qty"] = rng.choice(BAD_QUANTITIES)
        row["tags"].add("impossible")

    for row in dupes:
        row["tags"].add("dup")
        copy = dict(row, tags={"dup"}, copy=True)
        rows.append(copy)

    # Order IDs follow the real time each register saved the order.
    rows.sort(key=lambda r: (r["true_dt"], r["copy"]))
    for n, row in enumerate(rows, start=1):
        row["order_id"] = n

    # Write the database.
    out_path = Path(out_path)
    if out_path.exists():
        out_path.unlink()
    con = sqlite3.connect(out_path)
    con.executescript("""
        CREATE TABLE menu_items (
            item_id  INTEGER PRIMARY KEY,
            name     TEXT NOT NULL,
            category TEXT NOT NULL,
            price    REAL NOT NULL
        );
        CREATE TABLE orders (
            order_id    INTEGER PRIMARY KEY,
            ordered_at  TEXT NOT NULL,
            register_id INTEGER NOT NULL,
            item_id     INTEGER NOT NULL,
            quantity    INTEGER NOT NULL,
            unit_price  REAL NOT NULL
        );
    """)
    con.executemany("INSERT INTO menu_items VALUES (?, ?, ?, ?)", MENU)
    con.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        [(r["order_id"], r["stored_dt"].strftime("%Y-%m-%d %H:%M:%S"), r["register"],
          r["item"], r["qty"], r["price"]) for r in rows],
    )
    con.commit()
    con.close()

    # Ground truth for each case, in the same shape as the expected query output.
    def stamp(r):
        return r["stored_dt"].strftime("%Y-%m-%d %H:%M:%S")

    truth = {
        1: {(stamp(r), r["register"], r["item"], r["qty"], 2) for r in rows if "dup" in r["tags"]},
        2: {(r["order_id"], r["qty"]) for r in rows if "impossible" in r["tags"]},
        3: {(r["order_id"], r["price"]) for r in rows if "cents" in r["tags"]},
        4: {(r["order_id"], r["register"], stamp(r)) for r in rows
            if "tz" in r["tags"] and not 7 <= r["stored_dt"].hour <= 21},
        5: {(r["order_id"], r["item"]) for r in rows if "ghost" in r["tags"]},
    }
    info = {
        "seed": seed,
        "orders": len(rows),
        "cents_week": f"{days[cents_week * 7]} to {days[cents_week * 7 + 6]}",
        "tz_days": f"{days[tz_start]} to {days[tz_start + 3]} (register 2)",
        "ghost_item_id": ghost_id,
        "counts": {case: len(t) for case, t in truth.items()},
    }
    return truth, info


def write_check_data(db_path, out_path):
    """Fingerprint the reference answers so check.py can say PASS/FAIL without revealing them."""
    import json
    from detective_utils import CASES, fingerprint, read_query, run

    data = {}
    for case in CASES:
        sql = read_query(ROOT / "staff" / "solutions" / case["file"])
        _, rows = run(sql, db_path)
        data[str(case["id"])] = {"columns": case["columns"], "fingerprint": fingerprint(rows)}
    Path(out_path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=PUBLIC_SEED)
    parser.add_argument("--out", default=None, help="where to write the database")
    args = parser.parse_args()

    public = args.out is None and args.seed == PUBLIC_SEED
    out = Path(args.out) if args.out else ROOT / "kernel_cafe.db"
    _, info = build(args.seed, out)
    print(f"Wrote {out}")
    for key, value in info.items():
        print(f"  {key}: {value}")
    if public:
        write_check_data(out, ROOT / "check_data.json")
        print(f"Wrote {ROOT / 'check_data.json'}")


if __name__ == "__main__":
    main()
