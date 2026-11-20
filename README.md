# MP Data Detective: The Case of Kernel Café

## Start here

Kernel Café is a small coffee shop on campus, and its owner has a problem: the sales numbers feel off. Some days look too good, one week looks impossibly good, and the sales-by-hour chart shows customers buying lattes at 1 AM, when the café is closed.

The owner already asked an AI assistant to check the database. It ran one query and reported back:

> "I checked for duplicate orders. No duplicates found. Your data looks clean!"

The owner isn't convinced, and neither are we. **Your job is to investigate the sales database with SQL, crack five cases of bad data, and figure out where the AI went wrong.**

Allow about **2 hours** in total, including the videos. You don't need any SQL experience. Everything you need is in the videos, this README, and the [SQL cheat sheet](docs/cheatsheet.md).

## At a glance

| | |
| --- | --- |
| **What you'll learn** | Core SQL (SELECT, WHERE, GROUP BY/HAVING, aggregates, JOINs), common ways real data goes wrong, and how to check a query that looks right |
| **What you'll write** | Five SQL queries, one per case, plus two short written answers |
| **Tools** | Python 3.8 or newer. SQLite comes built into Python, so there is nothing else to install |
| **Submit** | Your five `.sql` files from `cases/`, the AI question, and the reflection, all on PrairieLearn |

| Part | Time |
| --- | --- |
| 4 short videos + comprehension questions | ~25 min |
| Setup | ~5 min |
| Cases 1 and 2 (guided, with hints) | ~20 min |
| Cases 3 to 5 (detective, symptoms only) | 45 to 60 min |
| The AI's report + reflection | ~15 min |

## Set up

Clone this repo (the link will be on PrairieLearn) and open a terminal in its folder:

```sh
git clone <repo link from PrairieLearn>
cd mp-data-detective
```

Check your Python version:

```sh
python --version
```

You need 3.8 or newer. On some Macs the command is `python3` instead of `python`. Use whichever one works everywhere below. If you don't have Python, install it from [python.org](https://www.python.org/downloads/).

Then run the setup check:

```sh
python run_query.py cases/example.sql
```

If you see a table of 10 orders, you're ready!

## The database

`kernel_cafe.db` holds one fall semester of sales: about 25,000 rows, from the first day of classes through finals week. It has two tables.

**`menu_items`**: one row per item on the menu.

| Column | Type | Meaning |
| --- | --- | --- |
| `item_id` | INTEGER | Unique ID for the item |
| `name` | TEXT | Item name |
| `category` | TEXT | `coffee`, `tea`, or `food` |
| `price` | REAL | Current price in dollars |

**`orders`**: one row per item sold. If someone buys a latte and a muffin, that's two rows.

| Column | Type | Meaning |
| --- | --- | --- |
| `order_id` | INTEGER | Unique ID for the row. Every row has its own, even a duplicate |
| `ordered_at` | TEXT | Date and time, as `YYYY-MM-DD HH:MM:SS` in Central time |
| `register_id` | INTEGER | Which register rang it up: `1` or `2` |
| `item_id` | INTEGER | Which menu item was sold. Matches `menu_items.item_id` |
| `quantity` | INTEGER | How many of the item |
| `unit_price` | REAL | Price charged for one item, in dollars |

### Café policies

These are facts about Kernel Café. Use them to spot data that can't be right.

- Open **7 AM to 10 PM**, every day
- Quantity on one row is always **1 to 10**
- Every item on the menu costs **under $10**

### The menu

| Coffee | Tea | Food |
| --- | --- | --- |
| Java Chip Latte ($5.25) | Hash Table Chai ($4.50) | Null Pointer Bagel ($3.25) |
| Kotlin Cold Brew ($4.75) | Matcha Merge Sort ($5.50) | Stack Overflow Muffin ($3.75) |
| Recursive Roast ($2.95) | | Binary Breakfast Burrito ($7.95) |
| Big-O Americano ($3.50) | | Boolean Brownie ($2.75) |

## How to investigate

1. **Explore.** Try small queries to see what's normal. You can type a query right in the terminal:

   ```sh
   python run_query.py -q "SELECT * FROM menu_items"
   ```

   Results show 25 rows by default. Add `--limit 100` to see more.

2. **Form a hypothesis.** What could cause the symptom? Video 3 covers the usual suspects.

3. **Write your query** in the case file, below the comments. Each file holds exactly one `SELECT` query.

4. **Run it and check it.**

   ```sh
   python run_query.py cases/case1_duplicates.sql   # see your results
   python check.py 1                                # check case 1
   python check.py                                  # check all five
   ```

### Rules for every case

- **Return exactly the columns listed**, in that order. Use `AS` to name a column, like `COUNT(*) AS copies`.
- **Row order doesn't matter.** No need for `ORDER BY` in your final answer.
- **Don't hardcode dates or IDs.** The grader runs your query on a **hidden copy** of the database with the same kinds of problems on different dates and rows. A query like `WHERE order_id IN (101, 245, 3310)` can pass `check.py` here and still score zero. Describe the problem, not the specific rows.
- Your queries can only read the data. Nothing you run can change or break the database.

## The cases

### Case 1: The Double Tap (guided)

> "Some days' revenue looks a little too high."

When a register gets double-tapped, it saves the same order twice. Both copies have the same `ordered_at`, `register_id`, `item_id`, and `quantity`, but each gets its own `order_id`. Group by those four columns and keep the groups that appear more than once.

**Return:** `ordered_at, register_id, item_id, quantity, copies` (one row per duplicated order, where `copies` is how many times it appears)

### Case 2: Impossible Receipts (guided)

> "A few receipts look impossible."

Compare the orders against the café policies above. Which column breaks a rule? Use `WHERE` to keep only the rows that break it.

**Return:** `order_id, quantity`

### Case 3: The 100x Week (detective)

> "Revenue for one week looks about 100x too high."

From here on, you only get the symptom. Investigate, then write one query that catches every affected row.

**Return:** `order_id, unit_price`

### Case 4: Night Owls (detective)

> "Our sales-by-hour chart has a bump in the middle of the night, but we close at 10 PM."

**Return:** `order_id, register_id, ordered_at` (every order logged while the café was closed)

### Case 5: Ghost Items (detective)

> "Sales by menu item don't add up to total revenue."

**Return:** `order_id, item_id` (every order whose item can't be found on the menu)

## The AI's report

Here is the exact query the owner's AI assistant ran before it declared the data clean:

```sql
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Run it yourself. It really does return 0 rows. But you found duplicates in Case 1!

**On PrairieLearn, answer in 2 to 3 sentences:** why did this query return 0 rows, and what should it have grouped by instead?

## Reflection

Answer on PrairieLearn. A few sentences each is plenty.

1. Which case was hardest to crack, and which query finally revealed the problem?
2. Case 4 only catches register 2's orders that landed outside opening hours. How would you find its other shifted orders, the ones that still look like normal hours?
3. What's one habit you'll use next time an AI hands you a query that looks right?

## Submit

On PrairieLearn, upload your five case files from `cases/` (keep the file names as they are), then answer the AI question and the reflection. Run `python check.py` one last time before you upload.

## AI policy

**Please don't use AI tools for this MP.** That includes chat assistants and coding agents, for writing queries, exploring the data, or answering the case, AI, or reflection questions. The whole point is for you to build the detective instinct yourself, and every case is a single query you can absolutely write by hand. We're trusting you on this one!

You **can** use the videos, the [cheat sheet](docs/cheatsheet.md), the [SQLite documentation](https://www.sqlite.org/lang.html), and course staff. We're happy to help!

## Grading

| Part | How it's graded | Weight |
| --- | --- | --- |
| Cases 1 to 5 | Each query runs on this database **and** the hidden copy. Full credit if the results match the answer key on both, ignoring row order | 80% (16% each) |
| The AI's report | Explains why the query returned 0 rows | 10% |
| Reflection | Completion | 10% |

## Troubleshooting

| What you see | What to do |
| --- | --- |
| `python: command not found` | Try `python3` instead. |
| `Can't find the database` | Run commands from this folder, the one with `kernel_cafe.db` in it. If you just cloned, run `cd mp-data-detective` first. |
| `This file has no query yet` | Write your query below the comments in the case file, then save. |
| `SQLite error: no such column` | Check the spelling against the tables above. If you joined two tables, write `orders.item_id` or use a table alias. |
| `SQLite error: near "...": syntax error` | Look just before the word it names. Common causes: a missing comma between columns, or a missing quote around a date. |
| `Found more than one statement` | Each case file holds one query. Delete any extra queries you used for exploring. |
| `columns should be: ...` | Rename or reorder your columns to match exactly, using `AS`. |
| `these N rows aren't the full answer yet` | Your query runs, but catches too many or too few rows. Look at what it returns and compare against the symptom. |

## Files

```
README.md               you are here
kernel_cafe.db          the Kernel Café database
cases/                  your five case files (the only files you edit) + example.sql
run_query.py            runs a query and prints the results
check.py                checks your cases against kernel_cafe.db
docs/cheatsheet.md      one-page SQL reference
detective_utils.py      helper code for the scripts (no need to open)
check_data.json         fingerprints check.py compares against (no need to open)
staff/                  database generator, reference solutions, grader (course staff only)
```
