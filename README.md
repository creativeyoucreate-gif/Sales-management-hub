# Sales Intelligence Hub

## About the Project

Sales Intelligence Hub is a simple sales management system that I built with help of AI like Claude, Co pilot and myself using **Python**, **PostgreSQL** and **Streamlit**.

A company usually has many branches, and each branch sells products to customers. Customers often do not pay the full amount at once, they pay in parts. This project helps to:

- Record the sales made by each branch
- Record every payment a customer makes
- Find out how much money is received and how much is still pending
- Show the totals in a dashboard with charts
- Practice 20 SQL questions on the same data

There are two types of users. A **Super Admin** can see and manage every branch. An **Admin** can only work with their own branch.

---

## Technologies Used

| Technology | Why I used it |
|------------|---------------|
| Python | To write the logic of the application |
| PostgreSQL | To store the data in tables |
| psycopg2 | To connect Python with PostgreSQL |
| Streamlit | To build the web pages without HTML or CSS |
| pandas | To show the data as tables and charts |

---

## Project Files

| File | What it does |
|------|--------------|
| `sqlsc.sql` | Creates the database tables, the triggers and the sample data. This is run first. |
| `db_connection.py` | Contains the database settings (host, user, password, database name) and the `run_query()` function that every other file uses to talk to the database. |
| `crud_operations.py` | Contains all the database functions such as login, add sale, add payment, view sales, delete, and the dashboard totals. CRUD means Create, Read, Update, Delete. |
| `sql_queries.py` | Contains the 20 SQL questions in Python and a function to run any one of them. It can also generate the `queries.sql` file. |
| `queries.sql` | The same 20 SQL questions written in one SQL file, so they can be run directly in PostgreSQL. |
| `app.py` | The main Streamlit application with the login page and all the other pages. This is the file that is run. |
| `usersdetails.txt` | A list of the demo usernames and passwords. |
| `README.md` | This file. |

### How the files work together

```
app.py  →  crud_operations.py / sql_queries.py  →  db_connection.py  →  PostgreSQL database
(screens)        (database functions)                (connection)        (created by sqlsc.sql)
```

When a button is clicked in the app, `app.py` calls a function from `crud_operations.py`. That function sends a query through `db_connection.py` to the PostgreSQL database and brings the result back to the screen.

---

## Database Design

The database has 4 tables.

| Table | What it stores |
|-------|----------------|
| `branches` | Branch name and the name of the branch admin |
| `users` | Username, password, role (Super Admin or Admin), email and the branch of the user |
| `customer_sales` | Date, customer name, mobile number, product name, gross sales, received amount, pending amount and status |
| `payment_splits` | Each payment of a sale: payment date, amount paid and payment method (Cash, UPI or Card) |

**Relationships**

- One branch has many users and many sales.
- One sale has many payments (a customer can pay in parts).

### Automatic features in the database

- **Pending amount:** `pending_amount` is a generated column. PostgreSQL calculates it as `gross_sales - received_amount`, so I never enter it manually.
- **Trigger on payment insert:** When a payment is added, a trigger adds up all the payments of that sale and updates `received_amount`. If the sale is fully paid, the status changes to **Close**, otherwise it stays **Open**.
- **Trigger on payment delete:** When a payment is deleted, the trigger calculates the amounts again and reopens the sale if needed.
- **Cascade delete:** When a sale is deleted, all its payments are deleted automatically.

### Business rule

If the same customer buys a different product, it is saved as a **separate sale**. I do not use "1st sale / 2nd sale" numbering for customers. Every purchase is one row with its own `sale_id`.

---

## How to Run the Project

### Step 1: Install the packages
```bash
pip install streamlit psycopg2-binary pandas
```

### Step 2: Create the database
```bash
createdb -U postgres project1
```
If `createdb` does not work, open `psql` and run `CREATE DATABASE project1;`

### Step 3: Create the tables and sample data
```bash
psql -U postgres -d project1 -f sqlsc.sql
```
At the end it shows the row count of each table: branches = 4, users = 5, customer_sales = 10, payment_splits = 12.

This script can be run again at any time. It deletes the old tables and creates them fresh. Note that any data added by hand will also be removed.

### Step 4: Add the database password
Open `db_connection.py` and change these lines:
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "your_postgres_password_here"
DB_NAME = "project1"
```

### Step 5: Test the connection
```bash
python db_connection.py
```
The message **Connected to PostgreSQL successfully!** should appear.

### Step 6: Start the application
```bash
streamlit run app.py
```
Then open **http://localhost:8501** in the browser.

---

## Login Details

| Role | Username | Password |
|------|----------|----------|
| Super Admin | superadmin | admin@123 |
| Admin (Chennai) | chennai_admin | chennai@123 |
| Admin (Delhi) | delhi_admin | delhi@123 |
| Admin (Bangalore) | blr_admin | blr@123 |
| Admin (Mumbai) | mum_admin | mum@123 |

---

## Pages in the Application

| Page | What it does |
|------|--------------|
| Dashboard | Shows total sales, gross sales, received amount and pending amount, a branch-wise sales chart and a payment method table |
| Add Sale | Adds a new customer sale |
| Add Payment | Records a payment for a sale that still has pending money. The amount cannot be more than the pending amount. |
| View Sales | Shows the list of sales |
| Pending Payments | Shows the sales that are still Open |
| Reports & SQL Queries | Shows the monthly sales chart, all payments, and the SQL Query Explorer |
| Delete Records | Deletes a sale or a payment (Super Admin only) |

### Super Admin and Admin

| Feature | Super Admin | Admin |
|---------|:-----------:|:-----:|
| View sales of all branches | Yes | No (own branch only) |
| Add a sale for any branch | Yes | No (own branch only) |
| Delete records | Yes | No |

---

## SQL Queries

I wrote 20 SQL questions in four groups:

1. **Basic queries** (Q1 to Q5): select all records, filter by status and branch
2. **Aggregation queries** (Q6 to Q10): SUM, COUNT and AVG
3. **Join-based queries** (Q11 to Q15): joining sales, branches and payments
4. **Financial tracking queries** (Q16 to Q20): pending above 5000, top 3 sales, best branch, monthly summary, payment method totals

They can be used in three ways:

- In the app: **Reports & SQL Queries** page, then **SQL Query Explorer**
- In the terminal: `psql -U postgres -d project1 -f queries.sql`
- To create `queries.sql` again from Python: `python sql_queries.py`

---

## Possible Improvements

- Store passwords in hashed form (for example with `bcrypt`). Right now they are saved as plain text, which is fine for learning but not for a real system.
- Add an edit option for sales and payments.
- Add a date filter and export to Excel for the reports.

---

## Conclusion

This project helped me to understand how a Python application connects to a PostgreSQL database, how triggers keep the data correct automatically, and how SQL queries are used to build real reports.
