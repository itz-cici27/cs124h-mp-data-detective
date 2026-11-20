-- Case 1: The Double Tap (reference solution, STAFF ONLY)
-- A double-tap saves the same order twice with a new order_id, so group on
-- everything except order_id and keep groups that appear more than once.

SELECT ordered_at, register_id, item_id, quantity, COUNT(*) AS copies
FROM orders
GROUP BY ordered_at, register_id, item_id, quantity
HAVING COUNT(*) > 1;
