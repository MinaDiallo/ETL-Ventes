-- Créer un schéma pour Airflow
CREATE SCHEMA IF NOT EXISTS airflow;

-- Création des tables pour les données de ventes

-- Table principale des ventes
CREATE TABLE IF NOT EXISTS sales_data (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    line_number INTEGER,
    order_date TIMESTAMP,
    status VARCHAR(50),
    quarter INTEGER,
    month INTEGER,
    year INTEGER,
    product_line VARCHAR(100),
    suggested_retail_price NUMERIC(10, 2),
    product_code VARCHAR(50),
    customer_name VARCHAR(100),
    phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    territory VARCHAR(50),
    contact_last_name VARCHAR(100),
    contact_first_name VARCHAR(100),
    deal_size VARCHAR(20),
    line_total NUMERIC(12, 2),
    margin NUMERIC(10, 2),
    margin_percentage NUMERIC(10, 2),
    order_year INTEGER,
    order_month INTEGER,
    order_day INTEGER,
    order_quarter INTEGER,
    order_day_of_week INTEGER
);

-- Table d'agrégation par client
CREATE TABLE IF NOT EXISTS customer_aggregations (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    total_orders INTEGER,
    total_sales NUMERIC(14, 2),
    total_quantity INTEGER,
    first_order TIMESTAMP,
    last_order TIMESTAMP,
    customer_lifetime_days INTEGER
);

-- Table d'agrégation par produit
CREATE TABLE IF NOT EXISTS product_aggregations (
    id SERIAL PRIMARY KEY,
    product_code VARCHAR(50),
    total_quantity INTEGER,
    total_revenue NUMERIC(14, 2),
    order_count INTEGER,
    customer_count INTEGER
);

-- Table d'agrégation temporelle
CREATE TABLE IF NOT EXISTS time_aggregations (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    line_total NUMERIC(14, 2),
    order_number INTEGER,
    customer_name INTEGER,
    quantity INTEGER
);

-- Table de métadonnées ETL
CREATE TABLE IF NOT EXISTS etl_metadata (
    id SERIAL PRIMARY KEY,
    load_timestamp TIMESTAMP,
    rows_loaded INTEGER,
    source VARCHAR(255)
);

-- Création d'index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_sales_order_number ON sales_data(order_number);
CREATE INDEX IF NOT EXISTS idx_sales_product_code ON sales_data(product_code);
CREATE INDEX IF NOT EXISTS idx_sales_customer_name ON sales_data(customer_name);
CREATE INDEX IF NOT EXISTS idx_sales_order_date ON sales_data(order_date);