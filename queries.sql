-- ============================================================
--  SALES INTELLIGENCE HUB - 20 SQL QUESTIONS (PostgreSQL)
--  Run:  psql -U postgres -d project1 -f queries.sql
--  (Load sqlsc.sql first so the demo data exists.)
-- ============================================================


-- ============================================================
--  BASIC QUERIES
-- ============================================================

-- Q1. Retrieve all records from the customer_sales table
SELECT * FROM customer_sales;

-- Q2. Retrieve all records from the branches table
SELECT * FROM branches;

-- Q3. Retrieve all records from the payment_splits table
SELECT * FROM payment_splits;

-- Q4. Display all sales with status = 'Open'
SELECT * FROM customer_sales WHERE status = 'Open';

-- Q5. Retrieve all sales belonging to the Chennai branch
SELECT cs.*
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';


-- ============================================================
--  AGGREGATION QUERIES
-- ============================================================

-- Q6. Total gross sales across all branches
SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;

-- Q7. Total received amount across all sales
SELECT SUM(received_amount) AS total_received FROM customer_sales;

-- Q8. Total pending amount across all sales
SELECT SUM(pending_amount) AS total_pending FROM customer_sales;

-- Q9. Total number of sales per branch
SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_name
ORDER BY b.branch_name;

-- Q10. Average gross sales amount
SELECT AVG(gross_sales) AS avg_gross_sales FROM customer_sales;


-- ============================================================
--  JOIN-BASED QUERIES
-- ============================================================

-- Q11. Sales details along with the branch name
SELECT cs.*, b.branch_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;

-- Q12. Sales details along with total payment received (payment_splits)
SELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales,
       COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales
ORDER BY cs.sale_id;

-- Q13. Branch-wise total gross sales (JOIN & GROUP BY)
SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC;

-- Q14. Sales along with the payment method used
SELECT cs.sale_id, cs.name, cs.product_name,
       ps.amount_paid, ps.payment_method
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_date;

-- Q15. Sales along with the branch admin name
SELECT cs.*, b.branch_name, b.branch_admin_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;


-- ============================================================
--  FINANCIAL TRACKING QUERIES
-- ============================================================

-- Q16. Sales where the pending amount is greater than 5000
SELECT *
FROM customer_sales
WHERE pending_amount > 5000
ORDER BY pending_amount DESC;

-- Q17. Top 3 highest gross sales
SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;

-- Q18. Branch with the highest total gross sales
SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;

-- Q19. Monthly sales summary (group by month & year)
SELECT EXTRACT(YEAR FROM date)::int  AS year,
       EXTRACT(MONTH FROM date)::int AS month,
       COUNT(*)                      AS total_sales,
       SUM(gross_sales)              AS total_gross_sales
FROM customer_sales
GROUP BY 1, 2
ORDER BY year, month;

-- Q20. Payment method-wise total collection (Cash / UPI / Card)
SELECT payment_method, SUM(amount_paid) AS total_collected
FROM payment_splits
GROUP BY payment_method
ORDER BY total_collected DESC;
