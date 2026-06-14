# 📊 Sales Intelligence Hub

A simple branch-based sales management system built with Python, MySQL, and Streamlit.

---

## 📁 Project Files

```
sales_hub/
├── app.py              ← Main web app (run this)
├── crud_operations.py  ← All database functions
├── db_connection.py    ← MySQL connection setup
├── sqlsc.sql           ← Database setup script (run this first)
└── usersdetails.txt    ← Login credentials reference
```

---

## 🚀 How to Run

### Step 1 — Install required packages
```bash
pip install streamlit mysql-connector-python pandas
```

### Step 2 — Set up the database
Open MySQL Workbench and run the `sqlsc.sql` file.
This creates all tables, triggers, and sample data automatically.

### Step 3 — Update your MySQL password
Open `db_connection.py` and update this line:
```python
"password": "your_mysql_password_here",
```

### Step 4 — Test the connection
```bash
python db_connection.py
```
You should see: ✅ Connected to MySQL successfully!

### Step 5 — Start the app
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

---

## 🧭 What Each Page Does

| Page | Description |
|------|-------------|
| 🏠 Dashboard | KPI summary, branch-wise sales chart, payment breakdown |
| ➕ Add Sale | Add a new customer sale |
| 💳 Add Payment | Record a payment for an existing sale |
| 📋 View Sales | View all sales (filter by branch for Super Admin) |
| ⏳ Pending Payments | See all unpaid/partially paid sales |
| 📊 Reports | Run predefined SQL queries and view monthly trend |
| 🗑️ Delete Records | Delete sales or payments *(Super Admin only)* |

---

## 👤 Role Differences

| Feature | Super Admin | Admin |
|---------|-------------|-------|
| See all branches | ✅ | ❌ (own branch only) |
| Add sale for any branch | ✅ | ❌ |
| Delete records | ✅ | ❌ |
| View all reports | ✅ | ✅ |

---

## ⚡ How Payments Work

1. You add a payment in **Add Payment**
2. A MySQL trigger automatically:
   - Updates the received amount on the sale
   - Marks the sale as **Closed** if fully paid
3. If you delete a payment, the trigger recalculates everything back

> You never need to update amounts manually — the database handles it!

---

## 🗄 Database Tables

| Table | What it stores |
|-------|---------------|
| `branches` | Branch names and admin names |
| `users` | Login accounts and roles |
| `customer_sales` | All sales transactions |
| `payment_splits` | Payments made against each sale |
