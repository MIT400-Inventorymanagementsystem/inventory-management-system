/* ===========================================================
   Inventory Management DB — Full DDL + Seed + Views + Procs + Trigger
   Tested on MariaDB 10.4 (XAMPP) and MySQL 8.x
   Safe to re-run (drops first, then recreates).
   =========================================================== */

-- 0) Create / select schema
CREATE DATABASE IF NOT EXISTS inventory_mgmt;
USE inventory_mgmt;

-- 1) Drop in dependency order (children first)
DROP TRIGGER  IF EXISTS trg_products_low_stock_after_update;
DROP VIEW     IF EXISTS v_low_stock;
DROP VIEW     IF EXISTS v_top_sellers;
DROP VIEW     IF EXISTS v_revenue_by_day;

DROP PROCEDURE IF EXISTS sp_add_sale_item;
DROP PROCEDURE IF EXISTS sp_create_sale;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS stock_alerts;
DROP TABLE IF EXISTS sale_details;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- 2) Master tables
CREATE TABLE categories (
  category_id   INT PRIMARY KEY AUTO_INCREMENT,
  category_name VARCHAR(100) NOT NULL,
  description   TEXT,
  CONSTRAINT uq_category_name UNIQUE(category_name)
) ENGINE=InnoDB;

CREATE TABLE suppliers (
  supplier_id    INT PRIMARY KEY AUTO_INCREMENT,
  supplier_name  VARCHAR(150) NOT NULL,
  contact_number VARCHAR(15),
  email          VARCHAR(100),
  address        TEXT
) ENGINE=InnoDB;

CREATE TABLE products (
  product_id        INT PRIMARY KEY AUTO_INCREMENT,
  product_name      VARCHAR(100) NOT NULL,
  category_id       INT NULL,
  supplier_id       INT NULL,
  unit_price        DECIMAL(10,2) NOT NULL,
  quantity_in_stock INT NOT NULL DEFAULT 0,
  reorder_level     INT NOT NULL DEFAULT 5,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prod_cat FOREIGN KEY (category_id)
    REFERENCES categories(category_id) ON DELETE SET NULL,
  CONSTRAINT fk_prod_sup FOREIGN KEY (supplier_id)
    REFERENCES suppliers(supplier_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE customers (
  customer_id   INT PRIMARY KEY AUTO_INCREMENT,
  customer_name VARCHAR(150) NOT NULL,
  phone_number  VARCHAR(15),
  email         VARCHAR(100),
  address       TEXT
) ENGINE=InnoDB;

CREATE TABLE sales (
  sale_id      INT PRIMARY KEY AUTO_INCREMENT,
  customer_id  INT,
  sale_date    DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(10,2) DEFAULT 0,
  CONSTRAINT fk_sales_cust FOREIGN KEY (customer_id)
    REFERENCES customers(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE sale_details (
  sale_detail_id INT PRIMARY KEY AUTO_INCREMENT,
  sale_id        INT NOT NULL,
  product_id     INT NOT NULL,
  quantity       INT NOT NULL,
  unit_price     DECIMAL(10,2) NOT NULL,
  subtotal       DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
  CONSTRAINT fk_sdetail_sale FOREIGN KEY (sale_id)
    REFERENCES sales(sale_id) ON DELETE CASCADE,
  CONSTRAINT fk_sdetail_prod FOREIGN KEY (product_id)
    REFERENCES products(product_id)
) ENGINE=InnoDB;

CREATE TABLE purchase_orders (
  purchase_id  INT PRIMARY KEY AUTO_INCREMENT,
  supplier_id  INT,
  order_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(10,2),
  CONSTRAINT fk_po_sup FOREIGN KEY (supplier_id)
    REFERENCES suppliers(supplier_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE users (
  user_id       INT PRIMARY KEY AUTO_INCREMENT,
  username      VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('admin','clerk','viewer') DEFAULT 'viewer',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- log table (built by trigger)
CREATE TABLE stock_alerts (
  alert_id     INT PRIMARY KEY AUTO_INCREMENT,
  product_id   INT NOT NULL,
  product_name VARCHAR(100) NOT NULL,
  shortage     INT NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3) Helpful indexes (no-op if they already exist)
CREATE INDEX ix_sd_product_qty ON sale_details(product_id, quantity);
CREATE INDEX ix_sales_date      ON sales(sale_date);

-- 4) Seed data (categories, suppliers, customers, products)
INSERT INTO categories (category_name, description) VALUES
  ('Beverages','Drinks and juices'),
  ('Snacks','Packaged snacks'),
  ('Dairy','Milk, cheese, yogurt'),
  ('Bakery','Bread & baked goods'),
  ('Produce','Fruit & vegetables'),
  ('Frozen','Frozen foods');

INSERT INTO suppliers (supplier_name, contact_number, email, address) VALUES
  ('Fresh Farms Ltd','0411111111','sales@freshfarms.com','21 Green Rd'),
  ('Oceanic Traders','0400000000','hello@oceanic.com','9 Bay Street'),
  ('City Foods','0499999999','order@cityfoods.com','17 King St'),
  ('Global Wholesale','0422222222','inbox@globalwholesale.com','88 Harbor Ave');

INSERT INTO customers (customer_name, phone_number, email, address) VALUES
  ('Aarav Shah','0401000000','aarav@example.com','7 King St'),
  ('Mia Wilson','0401000001','mia@example.com','10 River Way'),
  ('Oliver Smith','0401000002','oliver@example.com','2 Oak Lane'),
  ('Sophia Brown','0401000003','sophia@example.com','99 Elm Ave'),
  ('Liam Taylor','0401000004','liam@example.com','55 Maple Rd'),
  ('Noah Chen','0401000005','noah@example.com','3 Pine Ct'),
  ('Ava Patel','0401000006','ava@example.com','12 Cedar Dr'),
  ('Lucas Nguyen','0401000007','lucas@example.com','20 Willow Pl');

INSERT INTO products
  (product_name, category_id, supplier_id, unit_price, quantity_in_stock, reorder_level)
VALUES
  ('Sparkling Water 500ml', 1, 3, 3.50, 200, 30),
  ('Banana 1kg',           5, 1, 4.00,  80, 25),
  ('Orange Juice 1L',      1, 1, 3.50, 115, 20),
  ('Potato Chips 150g',    2, 4, 2.80, 120, 25),
  ('Cheddar Cheese 500g',  3, 2, 8.40,  60, 15),
  ('Full Milk 2L',         3, 2, 3.20,  90, 20),
  ('Sourdough Loaf',       4, 4, 5.90,  40, 10),
  ('Multi-Grain Loaf',     4, 4, 5.40,  50, 10),
  ('Greek Yogurt 1kg',     3, 2, 7.60,  45, 12),
  ('Wholemeal Bread',      4, 4, 3.60,  70, 12);

-- Some seed sales + details (with totals recalculated)
INSERT INTO sales (customer_id, sale_date, total_amount) VALUES
  (1, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 0),
  (2, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 0),
  (3, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 0),
  (1, CURDATE(), 0);

INSERT INTO sale_details (sale_id, product_id, quantity, unit_price) VALUES
  (1, 2, 1, 4.00), (1, 4, 2, 2.80), (1, 1, 2, 3.50),
  (2, 10, 2, 3.60), (2, 7, 1, 5.90),
  (3, 5, 1, 8.40),  (3, 6, 1, 3.20), (3, 1, 1, 3.50),
  (4, 3, 2, 3.50);

-- apply stock decrements for the seeded historical sales (keyed UPDATEs)
UPDATE products p
JOIN (
  SELECT product_id, SUM(quantity) AS qty_sold
  FROM sale_details GROUP BY product_id
) t ON p.product_id = t.product_id
SET p.quantity_in_stock = GREATEST(0, p.quantity_in_stock - t.qty_sold);

-- refresh per-sale totals from details
UPDATE sales s
JOIN (
  SELECT sale_id, SUM(subtotal) AS tot
  FROM sale_details GROUP BY sale_id
) t ON s.sale_id = t.sale_id
SET s.total_amount = t.tot;

-- 5) Views
CREATE VIEW v_top_sellers AS
SELECT
  p.product_id,
  p.product_name,
  SUM(sd.quantity) AS total_qty_sold,
  SUM(sd.subtotal) AS total_revenue
FROM sale_details sd
JOIN products p  ON p.product_id = sd.product_id
JOIN sales    s  ON s.sale_id    = sd.sale_id
GROUP BY p.product_id, p.product_name
ORDER BY total_qty_sold DESC, total_revenue DESC;

CREATE VIEW v_revenue_by_day AS
SELECT
  DATE(s.sale_date) AS sale_day,
  COUNT(*)          AS orders,
  SUM(s.total_amount) AS revenue
FROM sales s
GROUP BY DATE(s.sale_date)
ORDER BY sale_day;

CREATE VIEW v_low_stock AS
SELECT
  p.product_id,
  p.product_name,
  p.quantity_in_stock,
  p.reorder_level,
  (p.reorder_level - p.quantity_in_stock) AS shortage
FROM products p
WHERE p.quantity_in_stock <= p.reorder_level
ORDER BY shortage DESC;

-- 6) Stored procedures (transactional flow)
DELIMITER $$

CREATE PROCEDURE sp_create_sale (
  IN  p_customer_id INT,
  IN  p_sale_date   DATETIME,
  OUT p_sale_id     INT
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;
    INSERT INTO sales (customer_id, sale_date)
    VALUES (p_customer_id, COALESCE(p_sale_date, NOW()));
    SET p_sale_id = LAST_INSERT_ID();
  COMMIT;
END $$

CREATE PROCEDURE sp_add_sale_item (
  IN p_sale_id    INT,
  IN p_product_id INT,
  IN p_qty        INT
)
BEGIN
  DECLARE v_unit DECIMAL(10,2);

  IF p_qty IS NULL OR p_qty <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be > 0';
  END IF;

  SELECT unit_price INTO v_unit
  FROM products
  WHERE product_id = p_product_id
  LIMIT 1;

  IF v_unit IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unknown product_id';
  END IF;

  -- optional stock check (prevent negative)
  IF (SELECT quantity_in_stock FROM products WHERE product_id = p_product_id) < p_qty THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock';
  END IF;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;
    -- add line
    INSERT INTO sale_details (sale_id, product_id, quantity, unit_price)
    VALUES (p_sale_id, p_product_id, p_qty, v_unit);

    -- decrement stock (keyed)
    UPDATE products
    SET quantity_in_stock = quantity_in_stock - p_qty
    WHERE product_id = p_product_id;

    -- refresh sale total from details
    UPDATE sales s
    JOIN (
      SELECT sale_id, SUM(subtotal) AS tot
      FROM sale_details WHERE sale_id = p_sale_id
      GROUP BY sale_id
    ) t ON s.sale_id = t.sale_id
    SET s.total_amount = t.tot;
  COMMIT;
END $$
DELIMITER ;

-- 7) Trigger: log low stock after any product update
DELIMITER $$
CREATE TRIGGER trg_products_low_stock_after_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
  IF NEW.quantity_in_stock <= NEW.reorder_level THEN
    INSERT INTO stock_alerts (product_id, product_name, shortage, created_at)
    VALUES (NEW.product_id, NEW.product_name,
            (NEW.reorder_level - NEW.quantity_in_stock),
            NOW());
  END IF;
END $$
DELIMITER ;

-- 8) App users & least-privilege GRANTs (for demo)
CREATE USER IF NOT EXISTS 'app_admin'  @'localhost' IDENTIFIED BY 'admin123!';
CREATE USER IF NOT EXISTS 'app_staff'  @'localhost' IDENTIFIED BY 'staff123!';
CREATE USER IF NOT EXISTS 'app_viewer' @'localhost' IDENTIFIED BY 'viewer123!';

GRANT ALL PRIVILEGES ON inventory_mgmt.* TO 'app_admin'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE ON inventory_mgmt.sales        TO 'app_staff'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON inventory_mgmt.sale_details TO 'app_staff'@'localhost';
GRANT SELECT, UPDATE                    ON inventory_mgmt.products     TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.categories   TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.customers    TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.suppliers    TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.v_top_sellers  TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.v_revenue_by_day TO 'app_staff'@'localhost';
GRANT SELECT                            ON inventory_mgmt.v_low_stock     TO 'app_staff'@'localhost';

GRANT SELECT ON inventory_mgmt.products           TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.categories         TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.customers          TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.suppliers          TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.v_top_sellers      TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.v_revenue_by_day   TO 'app_viewer'@'localhost';
GRANT SELECT ON inventory_mgmt.v_low_stock        TO 'app_viewer'@'localhost';

FLUSH PRIVILEGES;

-- 9) (Optional) Quick sanity checks — you can run these as needed
-- SELECT * FROM v_top_sellers   LIMIT 10;
-- SELECT * FROM v_revenue_by_day;
-- SELECT * FROM v_low_stock;
-- CALL sp_create_sale(1, NULL, @new_id); SELECT @new_id;
-- CALL sp_add_sale_item(@new_id, 1, 2); CALL sp_add_sale_item(@new_id, 2, 1);
