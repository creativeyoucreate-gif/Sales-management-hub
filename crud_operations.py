# ============================================================
#  crud_operations.py
#  All the database functions the app needs, in plain steps.
#  Every function below calls run_query() from db_connection.py.
# ============================================================

from db_connection import run_query


# ==========================
#  BRANCH FUNCTIONS
# ==========================

def get_all_branches():
    query = "SELECT * FROM branches"
    return run_query(query)


def get_branch_by_id(branch_id):
    query = "SELECT * FROM branches WHERE branch_id = %s"
    rows = run_query(query, (branch_id,))
    if rows:
        return rows[0]
    else:
        return None


# ==========================
#  USER / AUTH FUNCTIONS
# ==========================

def login_user(username, password):
    """Returns the matching user row if the username/password are correct, else None."""
    query = """
        SELECT u.*, b.branch_name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.branch_id
        WHERE u.username = %s AND u.password = %s
    """
    rows = run_query(query, (username, password))

    if rows:
        return rows[0]
    else:
        return None


def get_all_users():
    query = """
        SELECT u.user_id, u.username, u.role, u.email, b.branch_name
        FROM users u
        LEFT JOIN branches b ON u.branch_id = b.branch_id
    """
    return run_query(query)


# ==========================
#  SALES FUNCTIONS
# ==========================

def add_sale(branch_id, sale_date, name, mobile_number, product_name, gross_sales):
    query = """
        INSERT INTO customer_sales
            (branch_id, date, name, mobile_number, product_name, gross_sales)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING sale_id
    """
    params = (branch_id, sale_date, name, mobile_number, product_name, gross_sales)
    new_row = run_query(query, params, fetch="one")

    if new_row:
        sale_id = new_row["sale_id"]
        print("Sale added! sale_id =", sale_id)
        return sale_id
    else:
        return None


def get_all_sales():
    query = """
        SELECT cs.*, b.branch_name
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        ORDER BY cs.date DESC
    """
    return run_query(query)


def get_sales_by_branch(branch_id):
    query = """
        SELECT cs.*, b.branch_name
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        WHERE cs.branch_id = %s
        ORDER BY cs.date DESC
    """
    return run_query(query, (branch_id,))


def get_pending_sales(branch_id=None):
    """Sales that are still 'Open' (not fully paid yet)."""

    if branch_id:
        # Someone asked only for one branch's pending sales
        query = """
            SELECT cs.*, b.branch_name
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.status = 'Open' AND cs.branch_id = %s
            ORDER BY cs.date DESC
        """
        return run_query(query, (branch_id,))
    else:
        # No branch given, so show pending sales for every branch
        query = """
            SELECT cs.*, b.branch_name
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.status = 'Open'
            ORDER BY cs.date DESC
        """
        return run_query(query)


# ==========================
#  PAYMENT FUNCTIONS
# ==========================

def add_payment(sale_id, payment_date, amount_paid, payment_method):
    """A database trigger automatically updates the sale's received_amount and status."""
    query = """
        INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
        VALUES (%s, %s, %s, %s)
        RETURNING payment_id
    """
    params = (sale_id, payment_date, amount_paid, payment_method)
    new_row = run_query(query, params, fetch="one")

    if new_row:
        payment_id = new_row["payment_id"]
        print("Payment recorded! payment_id =", payment_id)
        return payment_id
    else:
        return None


def get_payments_for_sale(sale_id):
    query = "SELECT * FROM payment_splits WHERE sale_id = %s ORDER BY payment_date"
    return run_query(query, (sale_id,))


def get_all_payments():
    query = """
        SELECT ps.*, cs.name AS customer_name, cs.gross_sales, b.branch_name
        FROM payment_splits ps
        JOIN customer_sales cs ON ps.sale_id = cs.sale_id
        JOIN branches b ON cs.branch_id = b.branch_id
        ORDER BY ps.payment_date DESC
    """
    return run_query(query)


def delete_payment(payment_id):
    """Deleting a payment also makes the trigger recalculate the sale's balance."""
    query = "DELETE FROM payment_splits WHERE payment_id = %s"
    return run_query(query, (payment_id,), fetch=False)


def delete_sale(sale_id):
    """Deleting a sale also deletes its payments (ON DELETE CASCADE in the schema)."""
    query = "DELETE FROM customer_sales WHERE sale_id = %s"
    return run_query(query, (sale_id,), fetch=False)


# ==========================
#  KPI / REPORT FUNCTIONS
# ==========================

def get_kpi_summary(branch_id=None):
    """The four big numbers shown at the top of the dashboard."""

    if branch_id:
        query = """
            SELECT COUNT(*) AS total_sales,
                   COALESCE(SUM(gross_sales), 0)     AS total_gross,
                   COALESCE(SUM(received_amount), 0) AS total_received,
                   COALESCE(SUM(pending_amount), 0)  AS total_pending
            FROM customer_sales
            WHERE branch_id = %s
        """
        return run_query(query, (branch_id,))
    else:
        query = """
            SELECT COUNT(*) AS total_sales,
                   COALESCE(SUM(gross_sales), 0)     AS total_gross,
                   COALESCE(SUM(received_amount), 0) AS total_received,
                   COALESCE(SUM(pending_amount), 0)  AS total_pending
            FROM customer_sales
        """
        return run_query(query)


def get_branch_wise_sales():
    query = """
        SELECT b.branch_name,
               COUNT(cs.sale_id)        AS total_sales,
               SUM(cs.gross_sales)      AS total_gross_sales,
               SUM(cs.received_amount)  AS total_received,
               SUM(cs.pending_amount)   AS total_pending
        FROM customer_sales cs
        JOIN branches b ON cs.branch_id = b.branch_id
        GROUP BY b.branch_name
        ORDER BY total_gross_sales DESC
    """
    return run_query(query)


def get_payment_method_summary():
    query = """
        SELECT payment_method,
               COUNT(*)         AS num_transactions,
               SUM(amount_paid) AS total_collected
        FROM payment_splits
        GROUP BY payment_method
        ORDER BY total_collected DESC
    """
    return run_query(query)


def get_monthly_sales_trend():
    query = """
        SELECT EXTRACT(YEAR FROM date)::int  AS year,
               EXTRACT(MONTH FROM date)::int AS month,
               SUM(gross_sales) AS total_gross_sales
        FROM customer_sales
        GROUP BY 1, 2
        ORDER BY year, month
    """
    return run_query(query)


# ============================================================
#  Quick test — run this file directly to try the functions
# ============================================================
if __name__ == "__main__":
    print("=== Branches ===")
    branches = get_all_branches()
    for branch in branches:
        print(branch)

    print("")
    print("=== KPI Summary (All Branches) ===")
    kpi = get_kpi_summary()
    if kpi:
        print(kpi[0])

    print("")
    print("=== Branch-Wise Sales ===")
    rows = get_branch_wise_sales()
    for row in rows:
        print(row)
