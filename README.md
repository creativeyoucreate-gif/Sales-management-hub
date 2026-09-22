# 📊 Sales Intelligence Hub

A simple branch-based sales management system built with Python, PostgreSQL, and Streamlit.

---

## 📁 Project Files

```
sales_hub/
├── app.py              ← Main web app (run this)
├── crud_operations.py  ← All database functions
├── db_connection.py    ← PostgreSQL connection setup
├── sqlsc.sql           ← Database setup script (run this first)
└── usersdetails.txt    ← Login credentials reference
```

---

## 🚀 How to Run

### Step 1 — Install required packages
```bash
pip install streamlit psycopg2-binary pandas
```

### Step 2 — Create the database
PostgreSQL can't create-and-switch-into a database in one script, so create it first from a terminal:
```bash
createdb -U postgres project1
```
(If `createdb` isn't on your PATH, open `psql` and run `CREATE DATABASE project1;` instead.)

### Step 3 — Load the schema and sample data
```bash
psql -U postgres -d project1 -f sqlsc.sql
```
This creates all tables, triggers, and sample data.

> **`sqlsc.sql` is safe to run again at any time.** It starts by dropping the four
> tables if they already exist, then rebuilds everything fresh. So if your data ever
> looks wrong or your login stops working, just re-run this command — it always
> leaves you with a clean, correct copy of the sample data.

### Step 4 — Update your PostgreSQL password
Open `db_connection.py` and update these lines near the top:
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "your_postgres_password_here"
DB_NAME = "project1"
```

### Step 5 — Test the connection
```bash
python db_connection.py
```
You should see: **Connected to PostgreSQL successfully!**

### Step 6 — Start the app
```bash
streamlit run app.py
```
Then open your browser at: **http://localhost:8501**

---

## 🔑 Login Credentials

| Role        | Username       | Password     |
|-------------|----------------|--------------|
| Super Admin | superadmin     | admin@123    |
| Admin       | chennai_admin  | chennai@123  |
| Admin       | delhi_admin    | delhi@123    |
| Admin       | blr_admin      | blr@123      |
| Admin       | mum_admin      | mum@123      |

If login fails with these exact credentials, run this to check the data actually
loaded:
```bash
psql -U postgres -d project1 -c "SELECT username, password FROM users;"
```
If that returns 0 rows, re-run Step 3.

---

## 🧭 What Each Page Does

| Page | Description |
|------|-------------|
| 🏠 Dashboard | KPI summary, branch-wise sales chart, payment breakdown |
| ➕ Add Sale | Add a new customer sale |
| 💳 Add Payment | Record a payment for an existing sale |
| 📋 View Sales | View all sales (filter by branch for Admins) |
| ⏳ Pending Payments | See all unpaid/partially paid sales |
| 📊 Reports & SQL Queries | Monthly sales trend chart + full payments list |
| 🗑️ Delete Records | Delete sales or payments *(Super Admin only)* |

---

## 👤 Role Differences

| Feature | Super Admin | Admin |
|---------|-------------|-------|
| See all branches | ✅ | ❌ (own branch only) |
| Add sale for any branch | ✅ | ❌ (own branch only) |
| Delete records | ✅ | ❌ |
| View all reports | ✅ | ✅ |

---

## ⚡ How Payments Work

1. You add a payment on the **Add Payment** page.
2. A PostgreSQL trigger function automatically:
   - Recalculates the sale's `received_amount`
   - Marks the sale as **Close** once it's fully paid
3. If you delete a payment, the trigger recalculates everything back.

> You never update `received_amount` or `pending_amount` manually — the database
> handles both.

---

## 🗄 Database Tables

| Table | What it stores |
|-------|---------------|
| `branches` | Branch names and admin names |
| `users` | Login accounts and roles |
| `customer_sales` | All sales transactions |
| `payment_splits` | Payments made against each sale |

---

## 🔒 A note on passwords

The `users.password` column stores plain-text passwords, which is fine for a local
learning project but not for anything real. If you take this further, hash
passwords (e.g. with `bcrypt`) before storing them and compare hashes in
`login_user()` instead of comparing plain text in SQL.
