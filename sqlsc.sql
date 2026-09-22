-- ============================================================
--  SALES INTELLIGENCE HUB - PostgreSQL Database Schema
-- ============================================================
--  How to use this file:
--
--  1. Create an empty database first (PostgreSQL can't create
--     a database and use it in the same script, unlike MySQL):
--
--         createdb -U postgres project1
--
--  2. Then load this whole file into that database:
--
--         psql -U postgres -d project1 -f sqlsc.sql
--
--  This script is SAFE TO RUN AGAIN AND AGAIN. Every time you run
--  it, it first deletes the four tables (if they exist) and then
--  rebuilds them from scratch with fresh sample data. That way you
--  never end up with old, empty, or half-loaded tables sitting
--  around from an earlier attempt.
-- ============================================================


-- ============================================================
-- STEP 0: Start clean
-- Remove any old version of these tables first.
-- CASCADE also removes the triggers and any data that depends on them.
-- ============================================================
DROP TABLE IF EXISTS payment_splits CASCADE;
DROP TABLE IF EXISTS customer_sales CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS branches CASCADE;


-- ============================================================
-- TABLE 1: branches
-- ============================================================
CREATE TABLE branches (
    branch_id         SERIAL PRIMARY KEY,
    branch_name       VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);


-- ============================================================
-- TABLE 2: users
-- role can only be 'Super Admin' or 'Admin' (a CHECK constraint,
-- PostgreSQL's simple version of MySQL's ENUM)
-- ============================================================
CREATE TABLE users (
    user_id   SERIAL PRIMARY KEY,
    username  VARCHAR(100) NOT NULL,
    password  VARCHAR(255) NOT NULL,
    branch_id INT REFERENCES branches(branch_id),
    role      VARCHAR(20) NOT NULL CHECK (role IN ('Super Admin', 'Admin')),
    email     VARCHAR(255) UNIQUE NOT NULL
);


-- ============================================================
-- TABLE 3: customer_sales
-- pending_amount is a generated column: PostgreSQL calculates
-- and stores it automatically as (gross_sales - received_amount).
-- You never insert or update it yourself.
-- ============================================================
CREATE TABLE customer_sales (
    sale_id          SERIAL PRIMARY KEY,
    branch_id        INT NOT NULL REFERENCES branches(branch_id),
    date             DATE NOT NULL,
    name             VARCHAR(100) NOT NULL,
    mobile_number    VARCHAR(15) UNIQUE NOT NULL,
    product_name     VARCHAR(30) NOT NULL,
    gross_sales      DECIMAL(12, 2) NOT NULL,
    received_amount  DECIMAL(12, 2) DEFAULT 0.00,
    pending_amount   DECIMAL(12, 2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status           VARCHAR(10) DEFAULT 'Open' CHECK (status IN ('Open', 'Close'))
);


-- ============================================================
-- TABLE 4: payment_splits
-- ON DELETE CASCADE: deleting a sale deletes its payments too,
-- so you never get an "orphaned payment" error.
-- ============================================================
CREATE TABLE payment_splits (
    payment_id     SERIAL PRIMARY KEY,
    sale_id        INT NOT NULL REFERENCES customer_sales(sale_id) ON DELETE CASCADE,
    payment_date   DATE NOT NULL,
    amount_paid    DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL
);


-- ============================================================
-- TRIGGER 1: runs after a payment is INSERTED
-- Recalculates the sale's received_amount and status automatically.
-- ============================================================
CREATE OR REPLACE FUNCTION after_payment_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Add up every payment made for this sale so far
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_splits
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;

    -- Close the sale if it's now fully paid, otherwise keep it open
    UPDATE customer_sales
    SET status = CASE
        WHEN (gross_sales - received_amount) <= 0 THEN 'Close'
        ELSE 'Open'
    END
    WHERE sale_id = NEW.sale_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
EXECUTE FUNCTION after_payment_insert();


-- ============================================================
-- TRIGGER 2: runs after a payment is DELETED
-- Recalculates the sale's received_amount and reopens it if needed.
-- ============================================================
CREATE OR REPLACE FUNCTION after_payment_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_splits
        WHERE sale_id = OLD.sale_id
    )
    WHERE sale_id = OLD.sale_id;

    UPDATE customer_sales
    SET status = CASE
        WHEN (gross_sales - received_amount) <= 0 THEN 'Close'
        ELSE 'Open'
    END
    WHERE sale_id = OLD.sale_id;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_payment_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
EXECUTE FUNCTION after_payment_delete();


-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO branches (branch_name, branch_admin_name) VALUES
('Chennai',   'Ravi Kumar'),
('Delhi',     'Priya Sharma'),
('Bangalore', 'Arjun Nair'),
('Mumbai',    'Sunita Patel');

INSERT INTO users (username, password, branch_id, role, email) VALUES
('superadmin',    'admin@123',   NULL, 'Super Admin', 'superadmin@company.com'),
('chennai_admin', 'chennai@123',    1, 'Admin',       'chennai@company.com'),
('delhi_admin',   'delhi@123',      2, 'Admin',       'delhi@company.com'),
('blr_admin',     'blr@123',        3, 'Admin',       'bangalore@company.com'),
('mum_admin',     'mum@123',        4, 'Admin',       'mumbai@company.com');

INSERT INTO customer_sales (branch_id, date, name, mobile_number, product_name, gross_sales) VALUES
(1, '2024-01-05', 'Arun Selvam',   '9876543210', 'DS',  45000.00),
(1, '2024-01-10', 'Meena Devi',    '9876543211', 'DA',  38000.00),
(2, '2024-01-12', 'Rohit Verma',   '9876543212', 'FSD', 55000.00),
(2, '2024-01-15', 'Anita Singh',   '9876543213', 'BA',  32000.00),
(3, '2024-02-01', 'Kiran Rao',     '9876543214', 'DS',  47000.00),
(3, '2024-02-05', 'Divya Nair',    '9876543215', 'DA',  41000.00),
(4, '2024-02-10', 'Suresh Patil',  '9876543216', 'FSD', 60000.00),
(4, '2024-02-15', 'Neha Joshi',    '9876543217', 'BA',  35000.00),
(1, '2024-03-01', 'Vijay Kumar',   '9876543218', 'DS',  50000.00),
(2, '2024-03-05', 'Preethi Reddy', '9876543219', 'FSD', 58000.00);

INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method) VALUES
(1,  '2024-01-05', 20000.00, 'UPI'),
(1,  '2024-01-20', 25000.00, 'Card'),
(2,  '2024-01-10', 15000.00, 'Cash'),
(2,  '2024-02-10', 10000.00, 'UPI'),
(3,  '2024-01-12', 30000.00, 'Card'),
(4,  '2024-01-15', 32000.00, 'Cash'),
(5,  '2024-02-01', 20000.00, 'UPI'),
(6,  '2024-02-05', 41000.00, 'Card'),
(7,  '2024-02-10', 25000.00, 'Cash'),
(8,  '2024-02-15', 35000.00, 'UPI'),
(9,  '2024-03-01', 30000.00, 'Card'),
(10, '2024-03-05', 20000.00, 'Cash');


-- ============================================================
-- VERIFY
-- Run after loading to confirm everything is actually there:
-- you should see branches=4, users=5, customer_sales=10, payment_splits=12
-- ============================================================
SELECT 'branches'       AS table_name, COUNT(*) AS row_count FROM branches
UNION ALL
SELECT 'users',          COUNT(*) FROM users
UNION ALL
SELECT 'customer_sales', COUNT(*) FROM customer_sales
UNION ALL
SELECT 'payment_splits', COUNT(*) FROM payment_splits;
