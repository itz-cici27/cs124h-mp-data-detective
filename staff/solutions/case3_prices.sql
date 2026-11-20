-- Case 3: The 100x Week (reference solution, STAFF ONLY)
-- Every menu item costs under $10, so a unit_price above 10 was saved in cents.
-- Students usually find the week first with SUM or MAX grouped by week, e.g.
--   SELECT strftime('%W', ordered_at) AS week, MAX(unit_price) FROM orders GROUP BY week;

SELECT order_id, unit_price
FROM orders
WHERE unit_price > 10;
