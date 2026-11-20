-- Case 5: Ghost Items (reference solution, STAFF ONLY)
-- A LEFT JOIN keeps every order; orders with no matching menu item get NULLs.

SELECT o.order_id, o.item_id
FROM orders AS o
LEFT JOIN menu_items AS m ON o.item_id = m.item_id
WHERE m.item_id IS NULL;
