-- ============================================================
--  SALES INTELLIGENCE HUB - MySQL Database Schema (FIXED)
--  Fixes:
--    1. ON DELETE CASCADE on payment_splits → allows sale deletion
--    2. after_payment_delete trigger → recalculates received_amount
--       when a payment is deleted
-- ============================================================

CREATE DATABASE IF NOT EXISTS sales_management_system_pro1;
USE sales_management_system_pro1;

-- ============================================================
-- TABLE 1: branches
-- ============================================================
CREATE TABLE IF NOT EXISTS branches (
    branch_id         INT AUTO_INCREMENT PRIMARY KEY,
    branch_name       VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

-- ============================================================
-- TABLE 2: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id   INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(100) NOT NULL,
    password  VARCHAR(255) NOT NULL,
    branch_id INT,
    role      ENUM('Super Admin', 'Admin') NOT NULL,
    email     VARCHAR(255) UNIQUE NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- ============================================================
-- TABLE 3: customer_sales
-- ============================================================
CREATE TABLE IF NOT EXISTS customer_sales (
    sale_id          INT AUTO_INCREMENT PRIMARY KEY,
    branch_id        INT NOT NULL,
    date             DATE NOT NULL,
    name             VARCHAR(100) NOT NULL,
    mobile_number    VARCHAR(15) UNIQUE NOT NULL,
    product_name     VARCHAR(30) NOT NULL,
    gross_sales      DECIMAL(12, 2) NOT NULL,
    received_amount  DECIMAL(12, 2) DEFAULT 0.00,
    -- Generated Column: auto-calculated, cannot insert manually
    pending_amount   DECIMAL(12, 2) AS (gross_sales - received_amount) STORED,
    status           ENUM('Open', 'Close') DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

-- ============================================================
-- TABLE 4: payment_splits
-- FIX: Added ON DELETE CASCADE so deleting a sale automatically
--      removes all its linked payments (no FK violation error)
-- ============================================================
CREATE TABLE IF NOT EXISTS payment_splits (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    sale_id        INT NOT NULL,
    payment_date   DATE NOT NULL,
    amount_paid    DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,

    -- ON DELETE CASCADE: if the parent sale is deleted,
    -- all its payments are automatically deleted too
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
        ON DELETE CASCADE
);

-- ============================================================
-- TRIGGER 1: After INSERT on payment_splits
-- Updates received_amount and status in customer_sales
-- ============================================================
DELIMITER $$

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
        SELECT COALESCE(SUM(amount_paid), 0)
        FROM payment_splits
        WHERE sale_id = NEW.sale_id
    )
    WHERE sale_id = NEW.sale_id;

    UPDATE customer_sales
    SET status = CASE
        WHEN (gross_sales - received_amount) <= 0 THEN 'Close'
        ELSE 'Open'
    END
    WHERE sale_id = NEW.sale_id;
END$$

-- ============================================================
-- TRIGGER 2: After DELETE on payment_splits  ← NEW
-- Recalculates received_amount when a payment is removed,
-- and reopens the sale if it now has a pending balance
-- ============================================================
CREATE TRIGGER after_payment_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
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
END$$

DELIMITER ;

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
-- ============================================================
SELECT 'branches'       AS table_name, COUNT(*) AS row_count FROM branches
UNION ALL
SELECT 'users',          COUNT(*) FROM users
UNION ALL
SELECT 'customer_sales', COUNT(*) FROM customer_sales
UNION ALL
SELECT 'payment_splits', COUNT(*) FROM payment_splits;