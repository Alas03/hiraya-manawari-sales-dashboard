-- =====================================================================
-- schema.sql
-- Database design for Hiraya Manawari (SQLite)
--
--   customers ---+
--   products  ---+--> order_items --> orders <-- dim_date
--                                       ^
--   customers --------------------------+
--
-- orders + order_items = FACT tables (the events: what was bought)
-- customers, products, dim_date = DIMENSION tables (descriptions)
-- =====================================================================

PRAGMA foreign_keys = ON;

-- Drop old versions so this file can be re-run safely
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ---------- DIMENSION: customers ----------
CREATE TABLE customers (
    customer_id  TEXT PRIMARY KEY,
    city         TEXT NOT NULL,
    province     TEXT NOT NULL,
    region       TEXT NOT NULL,
    signup_date  TEXT NOT NULL          -- 'YYYY-MM-DD'
);

-- ---------- DIMENSION: products ----------
CREATE TABLE products (
    product_id    TEXT PRIMARY KEY,
    product_name  TEXT NOT NULL,
    category      TEXT NOT NULL,
    price         REAL NOT NULL CHECK (price > 0)
);

-- ---------- DIMENSION: dates (one row per calendar day) ----------
CREATE TABLE dim_date (
    date_id         TEXT PRIMARY KEY,   -- 'YYYY-MM-DD'
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      TEXT NOT NULL,
    day_of_week     TEXT NOT NULL,      -- 'Monday' ... 'Sunday'
    day_of_week_no  INTEGER NOT NULL,   -- 1 = Monday ... 7 = Sunday
    is_weekend      INTEGER NOT NULL,   -- 1 = yes, 0 = no
    is_sale_day     INTEGER NOT NULL,   -- 9.9, 10.10, 11.11, 12.12
    is_payday       INTEGER NOT NULL    -- 15th and 30th
);

-- ---------- FACT: orders (one row per order) ----------
CREATE TABLE orders (
    order_id        TEXT PRIMARY KEY,
    order_date      TEXT NOT NULL REFERENCES dim_date(date_id),
    customer_id     TEXT NOT NULL REFERENCES customers(customer_id),
    payment_method  TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('Completed', 'Cancelled', 'Returned')),
    shipping_fee    REAL NOT NULL
);

-- ---------- FACT: order_items (one row per product in an order) ----------
CREATE TABLE order_items (
    item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    TEXT NOT NULL REFERENCES orders(order_id),
    product_id  TEXT NOT NULL REFERENCES products(product_id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  REAL NOT NULL CHECK (unit_price > 0)
);

-- ---------- INDEXES (make JOINs and filters fast) ----------
CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_items_order     ON order_items(order_id);
CREATE INDEX idx_items_product   ON order_items(product_id);
