# SQL Cheat Sheet

Everything you need for this MP, on one page. Try any example with:

```sh
python run_query.py -q "SELECT * FROM menu_items LIMIT 3"
```

## Picking columns and rows

```sql
SELECT name, price          -- which columns (* means all of them)
FROM menu_items             -- which table
WHERE price < 4             -- which rows to keep
ORDER BY price DESC         -- sort (ASC is smallest first, DESC is largest first)
LIMIT 5;                    -- only show the first 5 rows
```

| In `WHERE` | Example |
| --- | --- |
| Compare | `price = 4.5`, `price <> 4.5` (not equal), `<`, `<=`, `>`, `>=` |
| Combine | `category = 'tea' AND price > 5`, `item_id = 1 OR item_id = 2` |
| Ranges and lists | `price BETWEEN 3 AND 5`, `category IN ('tea', 'food')` |
| Missing values | `name IS NULL`, `name IS NOT NULL` (never `= NULL`) |

Text and dates go in **single quotes**: `'tea'`, `'2027-09-01'`.

## Naming columns

```sql
SELECT name, price * 2 AS double_price FROM menu_items;
```

`AS` gives a column a name. You'll need it whenever a case asks for a column like `copies`.

## Aggregates: one answer from many rows

| Function | Gives you |
| --- | --- |
| `COUNT(*)` | how many rows |
| `SUM(col)` | the total |
| `AVG(col)` | the average |
| `MIN(col)`, `MAX(col)` | the smallest and largest |

```sql
SELECT COUNT(*), SUM(quantity * unit_price) AS revenue FROM orders;
```

## GROUP BY and HAVING

`GROUP BY` splits rows into groups and runs the aggregate once per group.

```sql
-- How many rows each menu item has
SELECT item_id, COUNT(*) AS rows_sold
FROM orders
GROUP BY item_id;
```

`HAVING` filters **groups**, after grouping. `WHERE` filters **rows**, before grouping.

```sql
-- Only the items that appear on more than 3,000 rows
SELECT item_id, COUNT(*) AS rows_sold
FROM orders
GROUP BY item_id
HAVING COUNT(*) > 3000;
```

You can group by more than one column. Rows land in the same group only if they match on every one.

## Dates and times

`ordered_at` is text like `2027-09-14 08:15:42`. SQLite has helpers to pull pieces out of it.

| Expression | Result for `2027-09-14 08:15:42` |
| --- | --- |
| `DATE(ordered_at)` | `2027-09-14` (the day) |
| `strftime('%H', ordered_at)` | `08` (the hour, as text) |
| `strftime('%W', ordered_at)` | `37` (week of the year, weeks start Monday) |
| `strftime('%Y-%m', ordered_at)` | `2027-09` (the month) |

```sql
-- Revenue per day
SELECT DATE(ordered_at) AS day, SUM(quantity * unit_price) AS revenue
FROM orders
GROUP BY day;
```

`strftime` returns text, so compare it to text: `strftime('%H', ordered_at) < '12'`.

## Joining two tables

A **JOIN** lines up rows from two tables that share a value. This toy example uses two tables that aren't in the café database:

```
students                      majors
name   | major_id             major_id | major
-------+---------             ---------+-----------
Ana    | 1                    1        | CS
Ben    | 2                    2        | Stats
Cam    | 9
```

`INNER JOIN` (or just `JOIN`) keeps only the rows that have a match:

```sql
SELECT s.name, m.major
FROM students AS s
JOIN majors AS m ON s.major_id = m.major_id;
-- Ana | CS
-- Ben | Stats          (Cam disappears: there's no major 9)
```

`LEFT JOIN` keeps **every** row from the left table. When there's no match, the right table's columns come back as `NULL`:

```sql
SELECT s.name, m.major
FROM students AS s
LEFT JOIN majors AS m ON s.major_id = m.major_id;
-- Ana | CS
-- Ben | Stats
-- Cam | NULL           (kept, with nothing to match)
```

Add `WHERE m.major_id IS NULL` to keep only the rows that had no match.

`AS s` and `AS m` are short nicknames for the tables. Once two tables are joined, write `s.major_id` or `m.major_id` so SQL knows which one you mean.

## Order of the parts

A query's parts always go in this order. You can skip any part except `SELECT`.

```
SELECT ... FROM ... JOIN ... ON ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT ...
```
