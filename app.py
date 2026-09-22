# ============================================================
#  app.py  —  Streamlit Dashboard for Sales Intelligence Hub
#  Run with:  streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
from datetime import date
from crud_operations import (
    login_user, get_all_branches, add_sale, get_all_sales,
    get_sales_by_branch, get_pending_sales, add_payment,
    get_payments_for_sale, get_all_payments, get_kpi_summary,
    get_branch_wise_sales, get_payment_method_summary,
    get_monthly_sales_trend, delete_sale, delete_payment
)

st.set_page_config(page_title="Sales Intelligence Hub", page_icon="📊", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# ── Helpers ──────────────────────────────────────────────────
def to_df(rows):
    """Turn a list of database rows into a pandas table for display."""
    if rows:
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame()

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

    if role == "Admin":
        kpi = get_kpi_summary(branch_id)
    else:
        kpi = get_kpi_summary()

    if kpi:
        k = kpi[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 Total Sales",     k.get("total_sales", 0))
        c2.metric("💰 Gross Sales (₹)", f"₹{k.get('total_gross', 0):,.2f}")
        c3.metric("✅ Received (₹)",     f"₹{k.get('total_received', 0):,.2f}")
        c4.metric("⏳ Pending (₹)",      f"₹{k.get('total_pending', 0):,.2f}")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🏢 Branch-Wise Sales")
        bws = get_branch_wise_sales()
        if bws:
            df = to_df(bws)
            df["total_gross_sales"] = pd.to_numeric(df["total_gross_sales"], errors="coerce")
            st.bar_chart(df.set_index("branch_name")["total_gross_sales"])
        else:
            st.info("No sales yet.")

    with col_b:
        st.subheader("💳 Payment Method Breakdown")
        pm = get_payment_method_summary()
        if pm:
            st.dataframe(to_df(pm), use_container_width=True)
        else:
            st.info("No payments yet.")


def page_add_sale(role, branch_id):
    st.title("➕ Add Sale")

    # Build a simple list of branch names for the dropdown
    branches = get_all_branches()
    branch_names = []
    branch_name_to_id = {}
    for b in branches:
        branch_names.append(b["branch_name"])
        branch_name_to_id[b["branch_name"]] = b["branch_id"]

    if role == "Super Admin":
        chosen_branch_name = st.selectbox("Branch", branch_names)
        chosen_branch_id = branch_name_to_id[chosen_branch_name]
    else:
        # Admins can only add sales for their own branch
        chosen_branch_id = branch_id
        st.write("Branch: your assigned branch")

    with st.form("add_sale_form"):
        sale_date = st.date_input("Date", value=date.today())
        name = st.text_input("Customer Name")
        mobile_number = st.text_input("Mobile Number")
        product_name = st.text_input("Product Name")
        gross_sales = st.number_input("Gross Sales (₹)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("Add Sale")

    if submitted:
        if name and mobile_number and product_name and gross_sales > 0:
            add_sale(chosen_branch_id, sale_date, name, mobile_number, product_name, gross_sales)
            st.success("Sale added successfully!")
        else:
            st.error("Please fill in all fields.")


def page_add_payment(role, branch_id):
    st.title("💳 Add Payment")

    if role == "Super Admin":
        sales = get_all_sales()
    else:
        sales = get_sales_by_branch(branch_id)

    if not sales:
        st.info("No sales found yet.")
        return

    # Build a simple list of sale choices for the dropdown
    sale_labels = []
    label_to_sale_id = {}
    for s in sales:
        label = f"Sale #{s['sale_id']} - {s['name']} (Pending: ₹{s['pending_amount']})"
        sale_labels.append(label)
        label_to_sale_id[label] = s["sale_id"]

    chosen_label = st.selectbox("Select Sale", sale_labels)
    chosen_sale_id = label_to_sale_id[chosen_label]

    with st.form("add_payment_form"):
        payment_date = st.date_input("Payment Date", value=date.today())
        amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
        payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
        submitted = st.form_submit_button("Add Payment")

    if submitted:
        if amount_paid > 0:
            add_payment(chosen_sale_id, payment_date, amount_paid, payment_method)
            st.success("Payment recorded successfully!")
        else:
            st.error("Please enter an amount greater than 0.")


def page_view_sales(role, branch_id):
    st.title("📋 View Sales")

    if role == "Super Admin":
        sales = get_all_sales()
    else:
        sales = get_sales_by_branch(branch_id)

    st.dataframe(to_df(sales), use_container_width=True)


def page_pending(role, branch_id):
    st.title("⏳ Pending Payments")

    if role == "Super Admin":
        pending = get_pending_sales()
    else:
        pending = get_pending_sales(branch_id)

    st.dataframe(to_df(pending), use_container_width=True)


def page_reports():
    st.title("📊 Reports & SQL Queries")

    st.subheader("Monthly Sales Trend")
    trend = get_monthly_sales_trend()
    if trend:
        df = to_df(trend)
        # Build a readable "2024-01" style label for the chart
        df["month_label"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
        df["total_gross_sales"] = pd.to_numeric(df["total_gross_sales"], errors="coerce")
        st.bar_chart(df.set_index("month_label")["total_gross_sales"])
    else:
        st.info("No sales data yet.")

    st.subheader("All Payments")
    payments = get_all_payments()
    st.dataframe(to_df(payments), use_container_width=True)


def page_delete():
    st.title("🗑️ Delete Records")
    st.warning("This permanently deletes data. Use with care.")

    tab_sales, tab_payments = st.tabs(["Delete a Sale", "Delete a Payment"])

    with tab_sales:
        sales = get_all_sales()
        sale_labels = []
        label_to_sale_id = {}
        for s in sales:
            label = f"Sale #{s['sale_id']} - {s['name']} (₹{s['gross_sales']})"
            sale_labels.append(label)
            label_to_sale_id[label] = s["sale_id"]

        if sale_labels:
            chosen_label = st.selectbox("Select a sale to delete", sale_labels)
            if st.button("Delete Sale"):
                delete_sale(label_to_sale_id[chosen_label])
                st.success("Sale deleted.")
                st.rerun()
        else:
            st.info("No sales to delete.")

    with tab_payments:
        payments = get_all_payments()
        payment_labels = []
        label_to_payment_id = {}
        for p in payments:
            label = f"Payment #{p['payment_id']} - {p['customer_name']} (₹{p['amount_paid']})"
            payment_labels.append(label)
            label_to_payment_id[label] = p["payment_id"]

        if payment_labels:
            chosen_label = st.selectbox("Select a payment to delete", payment_labels)
            if st.button("Delete Payment"):
                delete_payment(label_to_payment_id[chosen_label])
                st.success("Payment deleted.")
                st.rerun()
        else:
            st.info("No payments to delete.")


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

    if page == "🏠 Dashboard":
        page_dashboard(role, branch_id)
    elif page == "➕ Add Sale":
        page_add_sale(role, branch_id)
    elif page == "💳 Add Payment":
        page_add_payment(role, branch_id)
    elif page == "📋 View Sales":
        page_view_sales(role, branch_id)
    elif page == "⏳ Pending Payments":
        page_pending(role, branch_id)
    elif page == "📊 Reports & SQL Queries":
        page_reports()
    elif page == "🗑️ Delete Records":
        page_delete()


# ── Entry point ───────────────────────────────────────────────
def main():
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login()

if __name__ == "__main__":
    main()
