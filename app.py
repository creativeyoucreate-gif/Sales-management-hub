# ============================================================
#  app.py  —  Streamlit Dashboard for Sales Intelligence Hub
#  Run with:  streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
from datetime import date
from db_connection import run_query
from crud_operations import (
    login_user, get_all_branches, add_sale, get_all_sales,
    get_sales_by_branch, get_pending_sales, add_payment,
    get_payments_for_sale, get_all_payments, get_kpi_summary,
    get_branch_wise_sales, get_payment_method_summary,
    get_monthly_sales_trend
)

st.set_page_config(page_title="Sales Intelligence Hub", page_icon="📊", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# ── Helpers ──────────────────────────────────────────────────
def to_df(rows):
    return pd.DataFrame(rows) if rows else pd.DataFrame()

def page_title(text):
    st.markdown(f"<h1 style='text-align:center'>{text}</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def center_col():
    _, col, _ = st.columns([1, 2, 1])
    return col


# ── Login ─────────────────────────────────────────────────────
def show_login():
    page_title("🔐 Sales Intelligence Hub")
    st.markdown("<p style='text-align:center;color:gray'>Login to continue</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with center_col():
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Login", use_container_width=True)

        if submit:
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")


# ── Pages ─────────────────────────────────────────────────────
def page_dashboard(role, branch_id):
    st.title("📊 Sales Intelligence Hub — Dashboard")

    kpi = get_kpi_summary(branch_id if role == "Admin" else None)
    if kpi and kpi[0]:
        k = kpi[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Total Sales",     k["total_sales"] or 0)
        c2.metric("💰 Gross Sales (₹)", f"₹{k['total_gross']    or 0:,.2f}")
        c3.metric("✅ Received (₹)",     f"₹{k['total_received'] or 0:,.2f}")
        c4.metric("⏳ Pending (₹)",      f"₹{k['total_pending']  or 0:,.2f}")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🏢 Branch-Wise Sales")
        bws = get_branch_wise_sales()
        if bws:
            df = to_df(bws)
            df["total_gross_sales"] = pd.to_numeric(df["total_gross_sales"], errors="coerce")
            st.bar_chart(df.set_index("branch_name")["total_gross_sales"])

    with col_b:
        st.subheader("💳 Payment Method Breakdown")
        pm = get_payment_method_summary()
        if pm:
            st.dataframe(to_df(pm), use_container_width=True)


def page_add_sale(role, branch_id):
    page_title("➕ Add New Sale")

    branches = get_all_branches()
    if not branches:
        st.warning("No branches found.")
        return

    if role == "Admin":
        branch_options = {b["branch_name"]: b["branch_id"] for b in branches if b["branch_id"] == branch_id}
    else:
        branch_options = {b["branch_name"]: b["branch_id"] for b in branches}

    with center_col():
        with st.form("add_sale_form"):
            selected_branch = st.selectbox("Branch", list(branch_options.keys()))
            sale_date       = st.date_input("Sale Date", value=date.today())
            customer_name   = st.text_input("Customer Name")
            mobile          = st.text_input("Mobile Number (10 digits)")
            product         = st.selectbox("Product", ["DS", "DA", "BA", "FSD"])
            gross           = st.number_input("Gross Sales Amount (₹)", min_value=0.0, step=500.0)
            submit          = st.form_submit_button("✅ Add Sale", use_container_width=True)

        if submit:
            if not customer_name or not mobile:
                st.error("Please fill in all fields.")
            else:
                result = add_sale(branch_options[selected_branch], sale_date, customer_name, mobile, product, gross)
                if result:
                    st.success(f"✅ Sale added! Sale ID: {result}")
                else:
                    st.error("❌ Failed. Mobile number may already exist.")


def page_add_payment(role, branch_id):
    page_title("💳 Add Payment for a Sale")

    sales = get_sales_by_branch(branch_id) if role == "Admin" else get_all_sales()
    if not sales:
        st.warning("No sales records found.")
        return

    sale_options = {f"#{s['sale_id']} — {s['name']} (₹{s['pending_amount']})": s["sale_id"]
                    for s in sales if float(s["pending_amount"]) > 0}
    if not sale_options:
        st.success("🎉 All sales are fully paid!")
        return

    with center_col():
        st.info("💡 Database trigger auto-updates received & pending amounts after payment.")

        with st.form("add_payment_form"):
            selected_sale = st.selectbox("Select Sale", list(sale_options.keys()))
            payment_date  = st.date_input("Payment Date", value=date.today())
            amount        = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
            method        = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
            submit        = st.form_submit_button("✅ Record Payment", use_container_width=True)

        if submit:
            sid     = sale_options[selected_sale]
            pending = float(next(s for s in sales if s["sale_id"] == sid)["pending_amount"])

            if amount <= 0:
                st.error("❌ Amount must be greater than 0.")
            elif amount > pending:
                st.error(f"❌ Amount ₹{amount:,.2f} exceeds pending balance ₹{pending:,.2f}.")
            else:
                result = add_payment(sid, payment_date, amount, method)
                if result:
                    st.success(f"✅ Payment recorded! ID: {result}")
                    st.dataframe(to_df(get_payments_for_sale(sid)), use_container_width=True)
                else:
                    st.error("❌ Failed to record payment.")


def page_view_sales(role, branch_id):
    page_title("📋 Sales Records")

    if role == "Admin":
        sales = get_sales_by_branch(branch_id)
    else:
        branches   = get_all_branches()
        branch_map = {"All Branches": None}
        branch_map.update({b["branch_name"]: b["branch_id"] for b in branches})
        selected = st.selectbox("Filter by Branch", list(branch_map.keys()))
        bid   = branch_map[selected]
        sales = get_all_sales() if bid is None else get_sales_by_branch(bid)

    df = to_df(sales)
    if df.empty:
        st.info("No sales records found.")
    else:
        st.dataframe(df, use_container_width=True, height=400)
        st.caption(f"Total records: {len(df)}")


def page_pending(role, branch_id):
    page_title("⏳ Pending Payments")

    df = to_df(get_pending_sales(branch_id if role == "Admin" else None))
    if df.empty:
        st.success("🎉 No pending payments!")
    else:
        st.warning(f"⚠️ {len(df)} sales have pending amounts.")
        st.dataframe(df[["sale_id", "name", "mobile_number",
                          "gross_sales", "received_amount", "pending_amount", "status"]],
                     use_container_width=True)
        st.metric("Total Pending", f"₹{df['pending_amount'].sum():,.2f}")


def page_reports():
    page_title("📊 Reports & SQL Queries")

    queries = {
        "Q9  — Sales Count Per Branch": """
            SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
            FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id
            GROUP BY b.branch_name ORDER BY total_sales DESC""",
        "Q13 — Branch-Wise Gross Sales": """
            SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
            FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id
            GROUP BY b.branch_name ORDER BY total_gross_sales DESC""",
        "Q16 — Sales With Pending > 5000":
            "SELECT sale_id,name,gross_sales,received_amount,pending_amount FROM customer_sales WHERE pending_amount>5000 ORDER BY pending_amount DESC",
        "Q17 — Top 3 Highest Gross Sales":
            "SELECT sale_id,name,product_name,gross_sales FROM customer_sales ORDER BY gross_sales DESC LIMIT 3",
        "Q18 — Highest Grossing Branch": """
            SELECT b.branch_name, SUM(cs.gross_sales) AS total
            FROM customer_sales cs JOIN branches b ON cs.branch_id=b.branch_id
            GROUP BY b.branch_name ORDER BY total DESC LIMIT 1""",
        "Q19 — Monthly Sales Summary": """
            SELECT YEAR(date) AS year, MONTHNAME(date) AS month,
            COUNT(sale_id) AS num_sales, SUM(gross_sales) AS total_gross
            FROM customer_sales GROUP BY YEAR(date),MONTH(date),MONTHNAME(date)
            ORDER BY year,MONTH(date)""",
        "Q20 — Payment Method Collection": """
            SELECT payment_method, COUNT(*) AS num_transactions,
            SUM(amount_paid) AS total_collected FROM payment_splits
            GROUP BY payment_method ORDER BY total_collected DESC""",
    }

    choice = st.selectbox("Choose a query to run", list(queries.keys()))
    if st.button("▶ Run Query"):
        rows = run_query(queries[choice])
        if rows:
            st.dataframe(to_df(rows), use_container_width=True)
        else:
            st.info("No data returned.")

    st.divider()
    st.subheader("📈 Monthly Sales Trend")
    trend = get_monthly_sales_trend()
    if trend:
        df = pd.DataFrame(trend)
        df["period"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        df["total_gross_sales"] = pd.to_numeric(df["total_gross_sales"], errors="coerce")
        st.line_chart(df.set_index("period")["total_gross_sales"])


def page_delete():
    page_title("🗑️ Delete Records")
    st.warning("⚠️ Deletions are permanent and cannot be undone.")

    tab1, tab2 = st.tabs(["🧾 Delete a Sale", "💸 Delete a Payment"])

    with tab1:
        sales = get_all_sales()
        if not sales:
            st.info("No sales found.")
        else:
            sale_options = {f"#{s['sale_id']} — {s['name']} (₹{s['gross_sales']})": s["sale_id"] for s in sales}
            sid      = sale_options[st.selectbox("Select Sale to Delete", list(sale_options.keys()), key="del_sale")]
            payments = get_payments_for_sale(sid)

            if payments:
                st.info(f"ℹ️ This sale has {len(payments)} linked payment(s) that will also be deleted.")
                st.dataframe(to_df(payments), use_container_width=True)

            if st.checkbox("I understand this will permanently delete the sale and all its payments.", key="confirm_sale"):
                if st.button("🗑️ Delete Sale"):
                    if payments:
                        run_query("DELETE FROM payment_splits WHERE sale_id = %s", (sid,), fetch=False)
                    result = run_query("DELETE FROM customer_sales WHERE sale_id = %s", (sid,), fetch=False)
                    if result is not None:
                        st.success(f"✅ Sale #{sid} deleted.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete sale.")

    with tab2:
        all_payments = get_all_payments()
        if not all_payments:
            st.info("No payments found.")
        else:
            pay_options = {
                f"#{p['payment_id']} — Sale #{p['sale_id']} | ₹{p['amount_paid']} via {p['payment_method']} on {p['payment_date']}": p["payment_id"]
                for p in all_payments
            }
            pid = pay_options[st.selectbox("Select Payment to Delete", list(pay_options.keys()), key="del_payment")]

            if st.checkbox("I understand this will permanently delete this payment.", key="confirm_payment"):
                if st.button("🗑️ Delete Payment"):
                    result = run_query("DELETE FROM payment_splits WHERE payment_id = %s", (pid,), fetch=False)
                    if result is not None:
                        st.success(f"✅ Payment #{pid} deleted.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete payment.")


# ── Dashboard shell ───────────────────────────────────────────
def show_dashboard():
    user      = st.session_state.user
    role      = user["role"]
    branch_id = user.get("branch_id")

    st.sidebar.title("📊 Sales Hub")
    st.sidebar.markdown(f"**User:** {user['username']}")
    st.sidebar.markdown(f"**Role:** {role}")
    if branch_id:
        st.sidebar.markdown(f"**Branch:** {user.get('branch_name', '')}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    pages = ["🏠 Dashboard", "➕ Add Sale", "💳 Add Payment",
             "📋 View Sales", "⏳ Pending Payments", "📊 Reports & SQL Queries"]
    if role == "Super Admin":
        pages.append("🗑️ Delete Records")

    page = st.sidebar.radio("Navigate to", pages)

    if   page == "🏠 Dashboard":             page_dashboard(role, branch_id)
    elif page == "➕ Add Sale":               page_add_sale(role, branch_id)
    elif page == "💳 Add Payment":            page_add_payment(role, branch_id)
    elif page == "📋 View Sales":             page_view_sales(role, branch_id)
    elif page == "⏳ Pending Payments":       page_pending(role, branch_id)
    elif page == "📊 Reports & SQL Queries":  page_reports()
    elif page == "🗑️ Delete Records":         page_delete()


# ── Entry point ───────────────────────────────────────────────
def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login()

if __name__ == "__main__":
    main()