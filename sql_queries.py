# ============================================================
#  sql_queries.py
#  The 20 assignment SQL questions (PostgreSQL syntax).
#  Used by app.py (Reports & SQL Queries page) and by
#  generate_queries_sql() to build queries.sql.
# ============================================================

from db_connection import run_query


QUERIES = [
    # ===================== BASIC =====================
    {
        "no": 1, "section": "Basic",
        "title": "Retrieve all records from the customer_sales table",
        "sql": "SELECT * FROM customer_sales;",
    },
    {
        "no": 2, "section": "Basic",
        "title": "Retrieve all records from the branches table",
        "sql": "SELECT * FROM branches;",
    },
    {
        "no": 3, "section": "Basic",
        "title": "Retrieve all records from the payment_splits table",
        "sql": "SELECT * FROM payment_splits;",
    },
    {
        "no": 4, "section": "Basic",
        "title": "Display all sales with status = 'Open'",
        "sql": "SELECT * FROM customer_sales WHERE status = 'Open';",
    },
    {
        "no": 5, "section": "Basic",
        "title": "Retrieve all sales belonging to the Chennai branch",
        "sql": """SELECT cs.*
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
WHERE b.branch_name = 'Chennai';""",
    },

    # ================== AGGREGATION ==================
    {
        "no": 6, "section": "Aggregation",
        "title": "Total gross sales across all branches",
        "sql": "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;",
    },
    {
        "no": 7, "section": "Aggregation",
        "title": "Total received amount across all sales",
        "sql": "SELECT SUM(received_amount) AS total_received FROM customer_sales;",
    },
    {
        "no": 8, "section": "Aggregation",
        "title": "Total pending amount across all sales",
        "sql": "SELECT SUM(pending_amount) AS total_pending FROM customer_sales;",
    },
    {
        "no": 9, "section": "Aggregation",
        "title": "Total number of sales per branch",
        "sql": """SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_name
ORDER BY b.branch_name;""",
    },
    {
        "no": 10, "section": "Aggregation",
        "title": "Average gross sales amount",
        "sql": "SELECT AVG(gross_sales) AS avg_gross_sales FROM customer_sales;",
    },

    # ====================== JOINS ====================
    {
        "no": 11, "section": "Join-Based",
        "title": "Sales details along with the branch name",
        "sql": """SELECT cs.*, b.branch_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;""",
    },
    {
        "no": 12, "section": "Join-Based",
        "title": "Sales details along with total payment received (payment_splits)",
        "sql": """SELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales,
       COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales
ORDER BY cs.sale_id;""",
    },
    {
        "no": 13, "section": "Join-Based",
        "title": "Branch-wise total gross sales (JOIN & GROUP BY)",
        "sql": """SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC;""",
    },
    {
        "no": 14, "section": "Join-Based",
        "title": "Sales along with the payment method used",
        "sql": """SELECT cs.sale_id, cs.name, cs.product_name,
       ps.amount_paid, ps.payment_method
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id, ps.payment_date;""",
    },
    {
        "no": 15, "section": "Join-Based",
        "title": "Sales along with the branch admin name",
        "sql": """SELECT cs.*, b.branch_name, b.branch_admin_name
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;""",
    },

    # ============== FINANCIAL TRACKING ===============
    {
        "no": 16, "section": "Financial Tracking",
        "title": "Sales where the pending amount is greater than 5000",
        "sql": """SELECT *
FROM customer_sales
WHERE pending_amount > 5000
ORDER BY pending_amount DESC;""",
    },
    {
        "no": 17, "section": "Financial Tracking",
        "title": "Top 3 highest gross sales",
        "sql": """SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;""",
    },
    {
        "no": 18, "section": "Financial Tracking",
        "title": "Branch with the highest total gross sales",
        "sql": """SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
FROM customer_sales cs
JOIN branches b ON cs.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;""",
    },
    {
        "no": 19, "section": "Financial Tracking",
        "title": "Monthly sales summary (group by month & year)",
        "sql": """SELECT EXTRACT(YEAR FROM date)::int  AS year,
       EXTRACT(MONTH FROM date)::int AS month,
       COUNT(*)                      AS total_sales,
       SUM(gross_sales)              AS total_gross_sales
FROM customer_sales
GROUP BY 1, 2
ORDER BY year, month;""",
    },
    {
        "no": 20, "section": "Financial Tracking",
        "title": "Payment method-wise total collection (Cash / UPI / Card)",
        "sql": """SELECT payment_method, SUM(amount_paid) AS total_collected
FROM payment_splits
GROUP BY payment_method
ORDER BY total_collected DESC;""",
    },
]


def get_query(number):
    """Return the query dict for question number 1-20."""
    for q in QUERIES:
        if q["no"] == number:
            return q
    return None


def run_sql_query(number):
    """Run question `number` against the database and return the rows."""
    q = get_query(number)
    if q is None:
        return None
    return run_query(q["sql"])


def generate_queries_sql(path="queries.sql"):
    """Write all 20 queries into one .sql file."""
    lines = [
        "-- ============================================================",
        "--  SALES INTELLIGENCE HUB - 20 SQL QUESTIONS (PostgreSQL)",
        "--  Run:  psql -U postgres -d project1 -f queries.sql",
        "--  (Load sqlsc.sql first so the demo data exists.)",
        "-- ============================================================",
        "",
    ]
    current = None
    for q in QUERIES:
        if q["section"] != current:
            current = q["section"]
            lines += ["", "-- ============================================================",
                      f"--  {current.upper()} QUERIES",
                      "-- ============================================================", ""]
        lines.append(f"-- Q{q['no']}. {q['title']}")
        lines.append(q["sql"])
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Wrote", path)


if __name__ == "__main__":
    generate_queries_sql()
