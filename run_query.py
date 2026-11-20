"""Run one SQL query against the Kernel Café database and print the results.

    python run_query.py cases/example.sql            run the query in a file
    python run_query.py cases/case1_duplicates.sql   run one of your cases
    python run_query.py -q "SELECT * FROM menu_items" run a quick query typed right here
    python run_query.py cases/example.sql --limit 100 show up to 100 rows (default 25)
"""

import argparse
import sys

from detective_utils import DEFAULT_DB, QueryError, clean_sql, format_table, read_query, run


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?", help="a .sql file containing one SELECT query")
    parser.add_argument("-q", "--query", help="a query to run instead of a file")
    parser.add_argument("--limit", type=int, default=25, help="how many rows to show (default 25)")
    parser.add_argument("--db", default=DEFAULT_DB, help="database to use (default kernel_cafe.db)")
    args = parser.parse_args()

    if not args.file and not args.query:
        parser.print_help()
        return 1

    try:
        sql = clean_sql(args.query) if args.query else read_query(args.file)
        if sql is None:
            print("This file has no query yet. Write a SELECT query below the comments and save the file.")
            return 1
        columns, rows = run(sql, args.db)
    except QueryError as e:
        print(e)
        return 1

    print(format_table(columns, rows, args.limit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
