# Sales Intelligence Hub

A simple branch-based sales management system I built using Python, PostgreSQL and Streamlit.

## Project Files

```
sales_hub/
├── app.py              # main web app (run this)
├── crud_operations.py  # all the database functions
├── db_connection.py    # PostgreSQL connection setup
├── sqlsc.sql           # database setup script
└── usersdetails.txt    # login credentials for reference
```

## How to Run

**1. Install the packages**
```bash
pip install streamlit psycopg2-binary pandas
```

**2. Create the database**

PostgreSQL can't create a database and switch into it inside one script, so create it first from the terminal:
```bash
createdb -U postgres project1
```
If `createdb` isn't on your PATH, open `psql` and run `CREATE DATABASE project1;` instead.

**3. Load the schema and sample data**
```bash
psql -U postgres -d project1 -f sqlsc.sql
```
This creates the tables, triggers and some sample data.

Note: you can run `sqlsc.sql` as many times as you want. It drops the four tables first and rebuilds everything, so if your data looks wrong or login stops working, just run it again.

**4. Set your PostgreSQL password**

Open `db_connection.py` and change these lines at the top:
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "your_postgres_password_here"
DB_NAME = "project1"
```

**5. Test the connection**
```bash
python db_connection.py
```
It should print `Connected to PostgreSQL successfully!`

**6. Start the app**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

## Login Credentials

| Role        | Username      | Password    |
|-------------|---------------|-------------|
| Super Admin | superadmin    | admin@123   |
| Admin       | chennai_admin | chennai@123 |
| Admin       | delhi_admin   | delhi@123   |
| Admin       | blr_admin     | blr@123     |
| Admin       | mum_admin     | mum@123     |

If login fails with these, check whether the data actually loaded:
```bash
psql -U postgres -d project1 -c "SELECT username, password FROM users;"
```
If it returns 0 rows, redo Step 3.

## What Each Page Does

| Page | What it does |
|------|--------------|
| Dashboard | KPI summary, branch-wise sales chart, payment breakdown |
| Add Sale | Add a new customer sale |
| Add Payment | Record a payment against an existing sale |
| View Sales | See all sales (admins can filter by branch) |
| Pending Payments | Shows all unpaid or partially paid sales |
| Reports & SQL Queries | Monthly sales trend chart and the full payments list |
| Delete Records | Delete sales or payments (Super Admin only) |

## Roles

| Feature | Super Admin | Admin |
|---------|-------------|-------|
| See all branches | Yes | No, own branch only |
| Add sale for any branch | Yes | No, own branch only |
| Delete records | Yes | No |
| View all reports | Yes | Yes |

## How Payments Work

1. You add a payment on the Add Payment page.
2. A PostgreSQL trigger then automatically recalculates the sale's `received_amount` and marks the sale as **Close** once it's fully paid.
3. If you delete a payment, the trigger recalculates everything again.

So you never have to update `received_amount` or `pending_amount` yourself, the database does it.

## Database Tables

| Table | What it stores |
|-------|----------------|
| `branches` | Branch names and admin names |
| `users` | Login accounts and roles |
| `customer_sales` | All the sales transactions |
| `payment_splits` | Payments made against each sale |

## A note on passwords

Right now `users.password` stores plain text. That's okay for a local learning project but not for anything real. For a real app you should hash the passwords (for example with `bcrypt`) and compare the hashes in `login_user()` instead of comparing plain text in SQL.
