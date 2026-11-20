"""Shared helpers for running and checking MP Data Detective queries.

You don't need to read or edit this file. run_query.py and check.py use it.
"""

import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "kernel_cafe.db"
CASES_DIR = ROOT / "cases"
CHECK_DATA = ROOT / "check_data.json"

# The five cases, the file each one lives in, and the exact columns it must return.
CASES = [
    {
        "id": 1,
        "file": "case1_duplicates.sql",
        "title": "The Double Tap",
        "columns": ["ordered_at", "register_id", "item_id", "quantity", "copies"],
    },
    {
        "id": 2,
        "file": "case2_impossible.sql",
        "title": "Impossible Receipts",
        "columns": ["order_id", "quantity"],
    },
    {
        "id": 3,
        "file": "case3_prices.sql",
        "title": "The 100x Week",
        "columns": ["order_id", "unit_price"],
    },
    {
        "id": 4,
        "file": "case4_night_owls.sql",
        "title": "Night Owls",
        "columns": ["order_id", "register_id", "ordered_at"],
    },
    {
        "id": 5,
        "file": "case5_ghost_items.sql",
        "title": "Ghost Items",
        "columns": ["order_id", "item_id"],
    },
]


class QueryError(Exception):
    """A problem with a query file that the student should fix."""


def strip_comments(text):
    """Remove -- line comments and /* block */ comments."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"--[^\n]*", "", text)


def read_query(path):
    """Return the single SELECT statement in a .sql file, or None if it's still empty."""
    path = Path(path)
    if not path.exists():
        raise QueryError(f"Can't find {path}. Check the file name and that you're in the right folder.")
    sql = strip_comments(path.read_text(encoding="utf-8")).strip()
    return clean_sql(sql)


def clean_sql(sql):
    """Validate one query string. Returns None for an empty query."""
    sql = sql.strip()
    if not sql:
        return None
    sql = sql.rstrip(";").strip()
    if ";" in sql:
        raise QueryError("Found more than one statement. Each case needs exactly one SELECT query.")
    first_word = sql.split(None, 1)[0].lower()
    if first_word not in ("select", "with"):
        raise QueryError("Your query should start with SELECT. This MP only reads the data, it never changes it.")
    return sql


def connect_readonly(db_path):
    """Open the database read-only, so a query can never change it."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise QueryError(f"Can't find the database at {db_path}.")
    return sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)


def run(sql, db_path=DEFAULT_DB):
    """Run a query and return (column names, rows)."""
    con = connect_readonly(db_path)
    try:
        cur = con.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
    except sqlite3.Error as e:
        raise QueryError(f"SQLite error: {e}") from None
    finally:
        con.close()
    return columns, rows


def normalize_columns(columns):
    return [c.strip().lower() for c in columns]


def _canon_value(v):
    # Round money to cents, and treat 5.0 and 5 as the same value.
    if isinstance(v, float):
        v = round(v, 2)
        if v == int(v):
            return int(v)
    return v


def fingerprint(rows):
    """A fingerprint of a result that ignores row order."""
    canon = sorted(json.dumps([_canon_value(v) for v in row]) for row in rows)
    return hashlib.sha256("\n".join(canon).encode("utf-8")).hexdigest()


def format_table(columns, rows, limit=25):
    """Format query results as a plain text table."""
    if not columns:
        return "(no columns)"
    shown = rows[:limit]
    cells = [[str(c) for c in columns]] + [["NULL" if v is None else str(v) for v in row] for row in shown]
    widths = [max(len(r[i]) for r in cells) for i in range(len(columns))]
    lines = []
    for n, r in enumerate(cells):
        lines.append(" | ".join(val.ljust(widths[i]) for i, val in enumerate(r)))
        if n == 0:
            lines.append("-+-".join("-" * w for w in widths))
    if len(rows) > limit:
        lines.append(f"... and {len(rows) - limit} more rows")
    lines.append(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")
    return "\n".join(lines)
