# ============================================================
#  crud_operations.py  (refactored)
# ============================================================

from db_connection import run_query


# ---------- tiny helper -------------------------------------------------
def _branch_filter(branch_id):
    """Returns (WHERE clause, params) only when branch_id is given."""
    if branch_id:
        return "WHERE branch_id = %s", (branch_id,)
    return "", ()
# ------------------------------------------------------------------------


# ==========================
#  BRANCH FUNCTIONS
# ==========================

def get_all_branches():
    return run_query("SELECT * FROM branches")

def get_branch_by_id(branch_id):
    return run_query("SELECT * FROM branches WHERE branch_id = %s", (branch_id,))


# ==========================
#  USER / AUTH FUNCTIONS
# ==========================

def login_user(username, password):
    """Returns the user row if credentials match, else None."""
    result = run_query("""
        SELECT u.*, b.branch_name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.branch_id
        WHERE u.username = %s AND u.password = %s
    """, (username, password))
    return result[0] if result else None

def get_all_users():
    return run_query("""
        SELECT u.user_id, u.username, u.role, u.email, b.branch_name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.branch_id
    """)


# ==========================
#  SALES FUNCTIONS
# ==========================

# Reusable base query for customer_sales + branch join
_SALES_BASE = """
    SELECT cs.*, b.branch_name
    FROM customer_sales cs
    JOIN branches b ON cs.branch_id = b.branch_id
"""

def add_sale(branch_id, date, name, mobile_number, product_name, gross_sales):
    sale_id = run_query("""
        INSERT INTO customer_sales
            (branch_id, date, name, mobile_number, product_name, gross_sales)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (branch_id, date, name, mobile_number, product_name, gross_sales), fetch=False)
    print(f"✅ Sale added! sale_id = {sale_id}")
    return sale_id

def get_all_sales():
    return run_query(_SALES_BASE + "ORDER BY cs.date DESC")

def get_sales_by_branch(branch_id):
    return run_query(_SALES_BASE + "WHERE cs.branch_id = %s ORDER BY cs.date DESC", (branch_id,))

def get_pending_sales(branch_id=None):
    where, params = _branch_filter(branch_id)
    extra = f"AND cs.branch_id = %s" if branch_id else ""
    return run_query(
        _SALES_BASE + f"WHERE cs.status = 'Open' {extra} ORDER BY cs.date DESC",
        (branch_id,) if branch_id else ()
    )


# ==========================
#  PAYMENT SPLIT FUNCTIONS
# ==========================

def add_payment(sale_id, payment_date, amount_paid, payment_method):
    """DB trigger auto-updates received_amount and status — no manual update needed."""
    payment_id = run_query("""
        INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
        VALUES (%s, %s, %s, %s)
    """, (sale_id, payment_date, amount_paid, payment_method), fetch=False)
    print(f"✅ Payment recorded! payment_id = {payment_id}")
    return payment_id

def get_payments_for_sale(sale_id):
    return run_query("SELECT * FROM payment_splits WHERE sale_id = %s ORDER BY payment_date", (sale_id,))

def get_all_payments():
    return run_query("""
        SELECT ps.*, cs.name AS customer_name, cs.gross_sales, b.branch_name
        FROM payment_splits ps
        JOIN customer_sales cs ON ps.sale_id = cs.sale_id
        JOIN branches b ON cs.branch_id = b.branch_id
        ORDER BY ps.payment_date DESC
    """)


# ==========================
#  FINANCIAL KPI FUNCTIONS
# ==========================

def get_kpi_summary(branch_id=None):
    where, params = _branch_filter(branch_id)
    return run_query(f"""
        SELECT COUNT(*) AS total_sales,
               SUM(gross_sales)      AS total_gross,
               SUM(received_amount)  AS total_received,
               SUM(pending_amount)   AS total_pending
        FROM customer_sales {where}
    """, params)

def get_branch_wise_sales():
    return run_query("""
        SELECT b.branch_name,
               COUNT(cs.sale_id)        AS total_sales,
               SUM(cs.gross_sales)      AS total_gross_sales,
               SUM(cs.received_amount)  AS total_received,
               SUM(cs.pending_amount)   AS total_pending
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        GROUP BY b.branch_name
        ORDER BY total_gross_sales DESC
    """)

def get_payment_method_summary():
    return run_query("""
        SELECT payment_method,
               COUNT(*)         AS num_transactions,
               SUM(amount_paid) AS total_collected
        FROM payment_splits
        GROUP BY payment_method
        ORDER BY total_collected DESC
    """)

def get_monthly_sales_trend():
    return run_query("""
        SELECT YEAR(date) AS year, MONTH(date) AS month,
               SUM(gross_sales) AS total_gross_sales
        FROM customer_sales
        GROUP BY YEAR(date), MONTH(date)
        ORDER BY year, month
    """)


# ============================================================
#  Quick test
# ============================================================
if __name__ == "__main__":
    print("=== Branches ===")
    for b in get_all_branches(): print(b)

    print("\n=== KPI Summary (All Branches) ===")
    kpi = get_kpi_summary()
    if kpi: print(kpi[0])

    print("\n=== Branch-Wise Sales ===")
    for row in get_branch_wise_sales(): print(row)



# # ============================================================
# #  crud_operations.py
# #  All Create / Read / Update / Delete functions for the project
# #  Beginners: Each function does ONE specific database task
# # ============================================================

# from db_connection import run_query


# # ==========================
# #  BRANCH FUNCTIONS
# # ==========================

# def get_all_branches():
#     """Returns a list of all branches."""
#     return run_query("SELECT * FROM branches")


# def get_branch_by_id(branch_id):
#     """Returns a single branch by its ID."""
#     return run_query("SELECT * FROM branches WHERE branch_id = %s", (branch_id,))


# # ==========================
# #  USER / AUTH FUNCTIONS
# # ==========================

# def login_user(username, password):
#     """
#     Checks username and password.
#     Returns the user row if valid, or None if invalid.

#     NOTE: In production, use hashed passwords (bcrypt).
#     This example uses plain text for simplicity.
#     """
#     query = """
#         SELECT u.*, b.branch_name
#         FROM users u
#         LEFT JOIN branches b ON u.branch_id = b.branch_id
#         WHERE u.username = %s AND u.password = %s
#     """
#     result = run_query(query, (username, password))
#     if result:
#         return result[0]   # Return first (and only) matching user
#     return None


# def get_all_users():
#     """Returns all users (Super Admin use only)."""
#     return run_query("""
#         SELECT u.user_id, u.username, u.role, u.email, b.branch_name
#         FROM users u
#         LEFT JOIN branches b ON u.branch_id = b.branch_id
#     """)


# # ==========================
# #  SALES FUNCTIONS
# # ==========================

# def add_sale(branch_id, date, name, mobile_number, product_name, gross_sales):
#     """
#     Adds a new customer sale record.

#     Note: received_amount starts at 0 (updated by trigger later)
#           pending_amount is auto-calculated by the Generated Column
#     """
#     query = """
#         INSERT INTO customer_sales
#             (branch_id, date, name, mobile_number, product_name, gross_sales)
#         VALUES (%s, %s, %s, %s, %s, %s)
#     """
#     params = (branch_id, date, name, mobile_number, product_name, gross_sales)
#     sale_id = run_query(query, params, fetch=False)
#     print(f"✅ Sale added! sale_id = {sale_id}")
#     return sale_id


# def get_all_sales():
#     """Super Admin: Returns all sales across all branches."""
#     return run_query("""
#         SELECT cs.*, b.branch_name
#         FROM customer_sales cs
#         JOIN branches b ON cs.branch_id = b.branch_id
#         ORDER BY cs.date DESC
#     """)


# def get_sales_by_branch(branch_id):
#     """Admin: Returns sales only for a specific branch."""
#     return run_query("""
#         SELECT cs.*, b.branch_name
#         FROM customer_sales cs
#         JOIN branches b ON cs.branch_id = b.branch_id
#         WHERE cs.branch_id = %s
#         ORDER BY cs.date DESC
#     """, (branch_id,))


# def get_pending_sales(branch_id=None):
#     """
#     Returns all Open (pending) sales.
#     If branch_id is given → only that branch's pending sales.
#     If branch_id is None  → all branches (Super Admin).
#     """
#     if branch_id:
#         return run_query("""
#             SELECT cs.*, b.branch_name
#             FROM customer_sales cs
#             JOIN branches b ON cs.branch_id = b.branch_id
#             WHERE cs.status = 'Open' AND cs.branch_id = %s
#         """, (branch_id,))
#     else:
#         return run_query("""
#             SELECT cs.*, b.branch_name
#             FROM customer_sales cs
#             JOIN branches b ON cs.branch_id = b.branch_id
#             WHERE cs.status = 'Open'
#         """)


# # ==========================
# #  PAYMENT SPLIT FUNCTIONS
# # ==========================

# def add_payment(sale_id, payment_date, amount_paid, payment_method):
#     """
#     Adds a payment record.
#     The DB trigger will automatically:
#     - Update received_amount in customer_sales
#     - Update status to 'Close' if fully paid
#     You do NOT need to update anything else manually!
#     """
#     query = """
#         INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
#         VALUES (%s, %s, %s, %s)
#     """
#     params = (sale_id, payment_date, amount_paid, payment_method)
#     payment_id = run_query(query, params, fetch=False)
#     print(f"✅ Payment recorded! payment_id = {payment_id}")
#     return payment_id


# def get_payments_for_sale(sale_id):
#     """Returns all payment records for a specific sale."""
#     return run_query("""
#         SELECT * FROM payment_splits
#         WHERE sale_id = %s
#         ORDER BY payment_date
#     """, (sale_id,))


# def get_all_payments():
#     """Returns all payments with customer and branch info."""
#     return run_query("""
#         SELECT ps.*, cs.name AS customer_name, cs.gross_sales,
#                b.branch_name
#         FROM payment_splits ps
#         JOIN customer_sales cs ON ps.sale_id = cs.sale_id
#         JOIN branches b ON cs.branch_id = b.branch_id
#         ORDER BY ps.payment_date DESC
#     """)


# # ==========================
# #  FINANCIAL KPI FUNCTIONS
# # ==========================

# def get_kpi_summary(branch_id=None):
#     """
#     Returns key financial numbers:
#     - Total Gross Sales
#     - Total Received Amount
#     - Total Pending Amount
#     Filters by branch if branch_id is given.
#     """
#     if branch_id:
#         return run_query("""
#             SELECT
#                 COUNT(*)                    AS total_sales,
#                 SUM(gross_sales)            AS total_gross,
#                 SUM(received_amount)        AS total_received,
#                 SUM(pending_amount)         AS total_pending
#             FROM customer_sales
#             WHERE branch_id = %s
#         """, (branch_id,))
#     else:
#         return run_query("""
#             SELECT
#                 COUNT(*)                    AS total_sales,
#                 SUM(gross_sales)            AS total_gross,
#                 SUM(received_amount)        AS total_received,
#                 SUM(pending_amount)         AS total_pending
#             FROM customer_sales
#         """)


# def get_branch_wise_sales():
#     """Returns total gross sales grouped by branch — for comparison charts."""
#     return run_query("""
#         SELECT b.branch_name,
#                COUNT(cs.sale_id)   AS total_sales,
#                SUM(cs.gross_sales) AS total_gross_sales,
#                SUM(cs.received_amount) AS total_received,
#                SUM(cs.pending_amount)  AS total_pending
#         FROM customer_sales cs
#         JOIN branches b ON cs.branch_id = b.branch_id
#         GROUP BY b.branch_name
#         ORDER BY total_gross_sales DESC
#     """)


# def get_payment_method_summary():
#     """Returns total collection per payment method (Cash / UPI / Card)."""
#     return run_query("""
#         SELECT payment_method,
#                COUNT(*)          AS num_transactions,
#                SUM(amount_paid)  AS total_collected
#         FROM payment_splits
#         GROUP BY payment_method
#         ORDER BY total_collected DESC
#     """)


# def get_monthly_sales_trend():
#     """Returns month-wise total gross sales for trend analysis."""
#     return run_query("""
#         SELECT
#             YEAR(date)  AS year,
#             MONTH(date) AS month,
#             SUM(gross_sales) AS total_gross_sales
#         FROM customer_sales
#         GROUP BY YEAR(date), MONTH(date)
#         ORDER BY year, month
#     """)


# # ============================================================
# #  Quick test — run this file to see sample output
# # ============================================================
# if __name__ == "__main__":
#     print("=== Branches ===")
#     for b in get_all_branches():
#         print(b)

#     print("\n=== KPI Summary (All Branches) ===")
#     kpi = get_kpi_summary()
#     if kpi:
#         print(kpi[0])

#     print("\n=== Branch-Wise Sales ===")
#     for row in get_branch_wise_sales():
#         print(row)
