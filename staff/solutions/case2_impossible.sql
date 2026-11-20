-- Case 2: Impossible Receipts (reference solution, STAFF ONLY)
-- Café policy: quantity per line is 1 to 10.

SELECT order_id, quantity
FROM orders
WHERE quantity < 1 OR quantity > 10;
