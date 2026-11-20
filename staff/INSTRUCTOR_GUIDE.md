# MP Data Detective: Instructor Guide (staff only)

Students investigate a synthetic SQLite sales database for Kernel Café and write one SQL query per planted data problem. They clone the student repo, work on their own laptops, and upload their case files to PrairieLearn. Every query is autograded on the public database and on a hidden check copy built with a different seed, so hardcoded answers fail. AI tools are not allowed (honor system). Total student time is about 2 hours.

**In a real offering, move this `staff/` folder to a private repo.** It holds the reference solutions and the hidden seed.

## Files

| File | What it is |
| --- | --- |
| `generate_db.py` | Builds `kernel_cafe.db` from a seed and writes `check_data.json`. Holds `PUBLIC_SEED`, `HIDDEN_SEED`, and the semester start date |
| `solutions/` | Reference query for each case |
| `grade.py` | Autograder. Runs a student's `cases/` folder on both databases. `--json` prints a PrairieLearn-friendly result |
| `selftest.py` | Pre-release test. Checks 32 seeds, the grader, hardcoded answers, and `check.py` |

```sh
python staff/generate_db.py     # rebuild kernel_cafe.db + check_data.json
python staff/selftest.py        # should end with "All checks passed."
python staff/grade.py cases/    # grade a folder of case files
```

## Answer key

Counts and dates below are for the default `PUBLIC_SEED` (124). The hidden copy has the same five problems in different places.

| Case | Planted problem | Public database | Reference query |
| --- | --- | --- | --- |
| 1. The Double Tap | A register double-tap saved orders twice: same `ordered_at`, `register_id`, `item_id`, `quantity`, new `order_id` | 39 duplicated orders (each `copies = 2`) | `GROUP BY ordered_at, register_id, item_id, quantity HAVING COUNT(*) > 1` |
| 2. Impossible Receipts | `quantity` of 0, negative, or above 10 | 22 rows | `WHERE quantity < 1 OR quantity > 10` |
| 3. The 100x Week | One Monday to Sunday week saved `unit_price` in cents (475 instead of 4.75) | Oct 4 to 10, 2027: 1,454 rows | `WHERE unit_price > 10` |
| 4. Night Owls | Register 2 logged UTC instead of Central for 4 days, so evening sales landed at 10 PM to 3 AM | Oct 18 to 21, 2027: 92 rows outside opening hours | `WHERE strftime('%H', ordered_at) < '07' OR strftime('%H', ordered_at) >= '22'` |
| 5. Ghost Items | Orders for a seasonal item (Pumpkin Spice Pointer) that was removed from `menu_items` | `item_id` 11: 34 rows | `LEFT JOIN menu_items ... WHERE m.item_id IS NULL` |

Each planted row has only one problem, and no two real orders share a timestamp, so every case has one clean answer.

### Other answers that earn full credit

- **Case 3:** `unit_price > 100`, or `JOIN menu_items m ... WHERE o.unit_price <> m.price`.
- **Case 4:** `strftime('%H', ordered_at) NOT BETWEEN '07' AND '21'`, or adding `AND register_id = 2`.
- **Case 5:** `WHERE item_id NOT IN (SELECT item_id FROM menu_items)`. Note that `WHERE item_id > 10` also passes, because the ghost ID is always 11 to 15. It's a weak answer, so mention the LEFT JOIN in feedback if you see it.

### Common mistakes

| Case | Mistake | What happens |
| --- | --- | --- |
| 1 | Grouping by `order_id` too (the AI's mistake) | 0 rows |
| 1 | Missing `AS copies` | Column name check fails |
| 2 | `quantity < 0` or `quantity <= 0 OR quantity >= 10` | Misses zeros, or wrongly includes 10 |
| 3 | Hardcoding the week's dates | Passes `check.py`, fails the hidden copy |
| 4 | `> '22'` or `BETWEEN '00' AND '06'` | Misses the 10 PM or 11 PM rows |
| 4 | Comparing the hour to a number, like `< 7` | `strftime` returns text, so the comparison is wrong |
| 5 | Using `JOIN` instead of `LEFT JOIN` | The ghost rows are dropped before the `WHERE` |

## The AI's report: answer and rubric

The AI ran `SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1`. `order_id` is unique for every row, including both copies of a double-tapped order, so every group has exactly one row and the query always returns 0. It should have grouped by the columns that describe the order itself (`ordered_at, register_id, item_id, quantity`) and left out the ID.

| Points | Answer |
| --- | --- |
| Full | Says `order_id` is unique even for duplicates (so each group has one row) **and** names the columns to group by instead |
| Half | Gets one of the two |
| None | Blank, or doesn't explain the 0 rows |

## Reflection notes

Graded on completion. For question 2, a strong answer notes that the shifted orders between 7 AM and 10 PM look normal on their own. Ways to find them: compare register 2's hourly pattern to register 1's for the same days (the morning rush shows up around 1 to 3 PM on register 2), or notice that `order_id` follows the real save order, so a shifted order's timestamp is out of order with its neighbors' IDs.

## Timing

| Part | Time |
| --- | --- |
| 4 videos + comprehension questions | ~25 min |
| Setup | ~5 min |
| Cases 1 and 2 | ~20 min |
| Cases 3 to 5 | 45 to 60 min |
| AI question + reflection | ~15 min |

## Videos

1. **Welcome to Kernel Café (~5 min):** the story, what a database is, a tour of both tables, why tables link by ID, setup.
2. **Asking Questions with SQL (~8 min):** SELECT, WHERE, ORDER BY, LIMIT, aggregates, GROUP BY and HAVING, date helpers.
3. **How Data Goes Wrong (~7 min):** the five usual suspects with real-world examples (not the planted rows), JOINs on a toy example, the symptom to hypothesis to query to evidence method, and why not to hardcode.
4. **Cracking the Case (~5 min):** repo tour, `run_query.py` and `check.py`, output columns, grading, AI policy, tips.

## Changing the data

- **Semester dates:** set `SEMESTER_START` (a Monday) in `generate_db.py`. Thanksgiving break and finals week are offsets from it, so check `THANKSGIVING_BREAK` and `FINALS_WEEK` too.
- **Seeds:** change `PUBLIC_SEED` or `HIDDEN_SEED` to move the planted problems.
- After any change, run `generate_db.py`, then `selftest.py`, then update the counts and dates in the answer key above.

## Before release

- [ ] Move `staff/` to a private repo and pick a new `HIDDEN_SEED`
- [ ] Set `SEMESTER_START` and regenerate
- [ ] `python staff/selftest.py` passes
- [ ] Publish the student repo (everything except `staff/`) and link it on PrairieLearn
- [ ] Set up a PrairieLearn file-upload question for the five case files and connect `grade.py --json` as its autograder
- [ ] Add the comprehension, AI, and reflection questions on PrairieLearn
- [ ] Playtest with 1 or 2 people who don't know SQL and confirm they finish in under 3 hours
- [ ] Record the four videos

## Known limitations

- Students download `kernel_cafe.db`, so a coding agent could open it and solve the cases directly. The no-AI rule is on the honor system, like MP Context's AI guidelines. The hidden copy only stops hardcoded answers, which a good AI wouldn't write anyway.
- Students who share a correct, general query will pass. The hidden copy catches hardcoded answers, not sharing.
- The grader checks results, not how students got there, so the written AI question and reflection carry the "do you understand it" signal.
