CREATE DATABASE IF NOT EXISTS revenue_intelligence;

USE revenue_intelligence;

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_type VARCHAR(10),
    assortment VARCHAR(10),
    competition_distance FLOAT,
    promo2 TINYINT
);

CREATE TABLE sales (
    sale_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    store_id INT,
    sale_date DATE,
    sales FLOAT,
    customers INT,
    promo TINYINT,
    holiday TINYINT,
    school_holiday TINYINT
);

CREATE TABLE inventory (

    inventory_id INT AUTO_INCREMENT PRIMARY KEY,

    product_id VARCHAR(50),

    current_stock INT,

    reorder_level INT,

    supplier_lead_time INT
);

CREATE TABLE competitors (

    competitor_id INT AUTO_INCREMENT PRIMARY KEY,

    product_id VARCHAR(50),

    competitor_name VARCHAR(100),

    competitor_price DECIMAL(12,2),

    our_price DECIMAL(12,2),

    capture_date DATE
);

