-- Case 4: Night Owls (reference solution, STAFF ONLY)
-- Open 7 AM to 10 PM, so any hour before 07 or from 22 on is impossible.
-- strftime returns a zero-padded string, so string comparison works.

SELECT order_id, register_id, ordered_at
FROM orders
WHERE strftime('%H', ordered_at) < '07'
   OR strftime('%H', ordered_at) >= '22';
