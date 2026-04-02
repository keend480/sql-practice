from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
from io import StringIO

app = Flask(__name__)
DB_PATH = "practice.db"

EXERCISES = [
    # --- BASIC SELECT ---
    {
        "id": 0, "title": "Select All Customers",
        "difficulty": "Beginner", "category": "SELECT",
        "description": "Retrieve all columns from the <code>customers</code> table.",
        "hint": "Use SELECT * to get all columns.",
        "solution": "SELECT * FROM customers"
    },
    {
        "id": 1, "title": "Customer Names Only",
        "difficulty": "Beginner", "category": "SELECT",
        "description": "Retrieve only the <code>first_name</code> and <code>last_name</code> columns from the <code>customers</code> table.",
        "hint": "List the column names after SELECT, separated by commas.",
        "solution": "SELECT first_name, last_name FROM customers"
    },
    {
        "id": 2, "title": "Product Names and Prices",
        "difficulty": "Beginner", "category": "SELECT",
        "description": "Retrieve the <code>name</code> and <code>price</code> from the <code>products</code> table.",
        "hint": "SELECT name, price FROM ...",
        "solution": "SELECT name, price FROM products"
    },
    {
        "id": 3, "title": "All Orders",
        "difficulty": "Beginner", "category": "SELECT",
        "description": "Retrieve all columns from the <code>orders</code> table.",
        "hint": "SELECT * FROM orders",
        "solution": "SELECT * FROM orders"
    },
    {
        "id": 4, "title": "Distinct Categories",
        "difficulty": "Beginner", "category": "SELECT",
        "description": "Retrieve a list of unique category <code>name</code>s from the <code>categories</code> table.",
        "hint": "Use SELECT DISTINCT.",
        "solution": "SELECT DISTINCT name FROM categories"
    },
    # --- WHERE ---
    {
        "id": 5, "title": "Products Under $20",
        "difficulty": "Beginner", "category": "WHERE",
        "description": "Find all products with a <code>price</code> less than 20.",
        "hint": "Use WHERE price < 20.",
        "solution": "SELECT * FROM products WHERE price < 20"
    },
    {
        "id": 6, "title": "Customer by Email",
        "difficulty": "Beginner", "category": "WHERE",
        "description": "Find the customer with <code>email</code> = 'alice@example.com'.",
        "hint": "Use WHERE email = 'alice@example.com'.",
        "solution": "SELECT * FROM customers WHERE email = 'alice@example.com'"
    },
    {
        "id": 7, "title": "Shipped Orders",
        "difficulty": "Beginner", "category": "WHERE",
        "description": "Find all orders with <code>status</code> = 'Shipped'.",
        "hint": "Use WHERE status = 'Shipped'.",
        "solution": "SELECT * FROM orders WHERE status = 'Shipped'"
    },
    {
        "id": 8, "title": "Products in Stock",
        "difficulty": "Beginner", "category": "WHERE",
        "description": "Find all products where <code>stock</code> is greater than 0.",
        "hint": "Use WHERE stock > 0.",
        "solution": "SELECT * FROM products WHERE stock > 0"
    },
    {
        "id": 9, "title": "High Value Orders",
        "difficulty": "Beginner", "category": "WHERE",
        "description": "Find all orders where <code>total_amount</code> is greater than 100.",
        "hint": "Use WHERE total_amount > 100.",
        "solution": "SELECT * FROM orders WHERE total_amount > 100"
    },
    # --- ORDER BY ---
    {
        "id": 10, "title": "Products by Price Ascending",
        "difficulty": "Beginner", "category": "ORDER BY",
        "description": "List all products ordered by <code>price</code> from lowest to highest.",
        "hint": "Use ORDER BY price ASC.",
        "solution": "SELECT * FROM products ORDER BY price ASC"
    },
    {
        "id": 11, "title": "Products by Price Descending",
        "difficulty": "Beginner", "category": "ORDER BY",
        "description": "List all products ordered by <code>price</code> from highest to lowest.",
        "hint": "Use ORDER BY price DESC.",
        "solution": "SELECT * FROM products ORDER BY price DESC"
    },
    {
        "id": 12, "title": "Customers Alphabetically",
        "difficulty": "Beginner", "category": "ORDER BY",
        "description": "List all customers ordered by <code>last_name</code> alphabetically (A-Z).",
        "hint": "Use ORDER BY last_name.",
        "solution": "SELECT * FROM customers ORDER BY last_name"
    },
    {
        "id": 13, "title": "Most Recent Orders",
        "difficulty": "Beginner", "category": "ORDER BY",
        "description": "List all orders sorted by <code>order_date</code> from newest to oldest.",
        "hint": "Use ORDER BY order_date DESC.",
        "solution": "SELECT * FROM orders ORDER BY order_date DESC"
    },
    {
        "id": 14, "title": "Top 5 Most Expensive Products",
        "difficulty": "Beginner", "category": "ORDER BY",
        "description": "Show the top 5 most expensive products (by <code>price</code>).",
        "hint": "Combine ORDER BY price DESC with LIMIT 5.",
        "solution": "SELECT * FROM products ORDER BY price DESC LIMIT 5"
    },
    # --- AGGREGATE FUNCTIONS ---
    {
        "id": 15, "title": "Count All Customers",
        "difficulty": "Beginner", "category": "Aggregates",
        "description": "Count the total number of customers.",
        "hint": "Use COUNT(*).",
        "solution": "SELECT COUNT(*) FROM customers"
    },
    {
        "id": 16, "title": "Average Product Price",
        "difficulty": "Beginner", "category": "Aggregates",
        "description": "Find the average <code>price</code> of all products.",
        "hint": "Use AVG(price).",
        "solution": "SELECT AVG(price) FROM products"
    },
    {
        "id": 17, "title": "Total Sales",
        "difficulty": "Beginner", "category": "Aggregates",
        "description": "Find the total sum of all <code>total_amount</code> in the orders table.",
        "hint": "Use SUM(total_amount).",
        "solution": "SELECT SUM(total_amount) FROM orders"
    },
    {
        "id": 18, "title": "Highest Product Price",
        "difficulty": "Beginner", "category": "Aggregates",
        "description": "Find the highest <code>price</code> among all products.",
        "hint": "Use MAX(price).",
        "solution": "SELECT MAX(price) FROM products"
    },
    {
        "id": 19, "title": "Lowest Product Price",
        "difficulty": "Beginner", "category": "Aggregates",
        "description": "Find the lowest <code>price</code> among all products.",
        "hint": "Use MIN(price).",
        "solution": "SELECT MIN(price) FROM products"
    },
    # --- GROUP BY ---
    {
        "id": 20, "title": "Orders Per Customer",
        "difficulty": "Intermediate", "category": "GROUP BY",
        "description": "Count the number of orders placed by each <code>customer_id</code>.",
        "hint": "GROUP BY customer_id, then COUNT(*).",
        "solution": "SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id"
    },
    {
        "id": 21, "title": "Products Per Category",
        "difficulty": "Intermediate", "category": "GROUP BY",
        "description": "Count how many products belong to each <code>category_id</code>.",
        "hint": "GROUP BY category_id with COUNT(*).",
        "solution": "SELECT category_id, COUNT(*) as product_count FROM products GROUP BY category_id"
    },
    {
        "id": 22, "title": "Total Revenue Per Customer",
        "difficulty": "Intermediate", "category": "GROUP BY",
        "description": "Find the total <code>total_amount</code> spent by each <code>customer_id</code>.",
        "hint": "GROUP BY customer_id with SUM(total_amount).",
        "solution": "SELECT customer_id, SUM(total_amount) as total_spent FROM orders GROUP BY customer_id"
    },
    {
        "id": 23, "title": "Average Price Per Category",
        "difficulty": "Intermediate", "category": "GROUP BY",
        "description": "Find the average product price for each <code>category_id</code>.",
        "hint": "GROUP BY category_id with AVG(price).",
        "solution": "SELECT category_id, AVG(price) as avg_price FROM products GROUP BY category_id"
    },
    {
        "id": 24, "title": "Orders By Status",
        "difficulty": "Intermediate", "category": "GROUP BY",
        "description": "Count the number of orders grouped by <code>status</code>.",
        "hint": "GROUP BY status with COUNT(*).",
        "solution": "SELECT status, COUNT(*) as count FROM orders GROUP BY status"
    },
    # --- HAVING ---
    {
        "id": 25, "title": "Customers With Many Orders",
        "difficulty": "Intermediate", "category": "HAVING",
        "description": "Find customers who have placed more than 2 orders.",
        "hint": "Use GROUP BY customer_id, COUNT(*), then HAVING COUNT(*) > 2.",
        "solution": "SELECT customer_id, COUNT(*) as order_count FROM orders GROUP BY customer_id HAVING COUNT(*) > 2"
    },
    {
        "id": 26, "title": "High Revenue Categories",
        "difficulty": "Intermediate", "category": "HAVING",
        "description": "Find category_ids where the average product price is above 50.",
        "hint": "GROUP BY category_id, use HAVING AVG(price) > 50.",
        "solution": "SELECT category_id, AVG(price) as avg_price FROM products GROUP BY category_id HAVING AVG(price) > 50"
    },
    {
        "id": 27, "title": "Big Spenders",
        "difficulty": "Intermediate", "category": "HAVING",
        "description": "Find customers who have spent more than $500 total across all orders.",
        "hint": "SUM(total_amount) per customer_id, then HAVING SUM > 500.",
        "solution": "SELECT customer_id, SUM(total_amount) as total FROM orders GROUP BY customer_id HAVING SUM(total_amount) > 500"
    },
    {
        "id": 28, "title": "Popular Categories",
        "difficulty": "Intermediate", "category": "HAVING",
        "description": "Find category_ids that have more than 3 products.",
        "hint": "COUNT(*) per category_id, HAVING COUNT(*) > 3.",
        "solution": "SELECT category_id, COUNT(*) as cnt FROM products GROUP BY category_id HAVING COUNT(*) > 3"
    },
    {
        "id": 29, "title": "High Order Status Groups",
        "difficulty": "Intermediate", "category": "HAVING",
        "description": "Find order statuses that appear more than 5 times.",
        "hint": "GROUP BY status, HAVING COUNT(*) > 5.",
        "solution": "SELECT status, COUNT(*) as cnt FROM orders GROUP BY status HAVING COUNT(*) > 5"
    },
    # --- JOINS ---
    {
        "id": 30, "title": "Orders With Customer Names",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List all orders along with the customer's <code>first_name</code> and <code>last_name</code>.",
        "hint": "JOIN orders with customers ON customer_id.",
        "solution": "SELECT o.*, c.first_name, c.last_name FROM orders o JOIN customers c ON o.customer_id = c.id"
    },
    {
        "id": 31, "title": "Products With Category Names",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List all products along with their category <code>name</code>.",
        "hint": "JOIN products with categories ON category_id.",
        "solution": "SELECT p.*, cat.name as category_name FROM products p JOIN categories cat ON p.category_id = cat.id"
    },
    {
        "id": 32, "title": "Order Items With Product Names",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List all order items along with the product <code>name</code>.",
        "hint": "JOIN order_items with products ON product_id.",
        "solution": "SELECT oi.*, p.name as product_name FROM order_items oi JOIN products p ON oi.product_id = p.id"
    },
    {
        "id": 33, "title": "Customer Order Summary",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List each customer's <code>first_name</code>, <code>last_name</code>, and the total number of orders they've placed.",
        "hint": "JOIN customers with orders, GROUP BY customer id.",
        "solution": "SELECT c.first_name, c.last_name, COUNT(o.id) as order_count FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.first_name, c.last_name"
    },
    {
        "id": 34, "title": "Customers With No Orders",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "Find customers who have not placed any orders.",
        "hint": "Use a LEFT JOIN and filter WHERE order id IS NULL.",
        "solution": "SELECT c.* FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.id IS NULL"
    },
    {
        "id": 35, "title": "Full Order Details",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List order items with the order <code>order_date</code>, product <code>name</code>, quantity, and unit_price.",
        "hint": "Join order_items with both orders and products.",
        "solution": "SELECT o.order_date, p.name, oi.quantity, oi.unit_price FROM order_items oi JOIN orders o ON oi.order_id = o.id JOIN products p ON oi.product_id = p.id"
    },
    {
        "id": 36, "title": "Products Never Ordered",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "Find products that have never appeared in any order.",
        "hint": "LEFT JOIN products with order_items, filter WHERE order_items.id IS NULL.",
        "solution": "SELECT p.* FROM products p LEFT JOIN order_items oi ON p.id = oi.product_id WHERE oi.id IS NULL"
    },
    {
        "id": 37, "title": "Order Items With Category",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List order items with the product name and its category name.",
        "hint": "Join order_items -> products -> categories.",
        "solution": "SELECT oi.*, p.name as product_name, cat.name as category_name FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN categories cat ON p.category_id = cat.id"
    },
    {
        "id": 38, "title": "Revenue By Category",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "Find total revenue (sum of unit_price * quantity) per category name.",
        "hint": "Join order_items -> products -> categories, then SUM(unit_price * quantity) GROUP BY category.",
        "solution": "SELECT cat.name, SUM(oi.unit_price * oi.quantity) as revenue FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN categories cat ON p.category_id = cat.id GROUP BY cat.id, cat.name"
    },
    {
        "id": 39, "title": "Top Selling Products",
        "difficulty": "Intermediate", "category": "JOIN",
        "description": "List the top 5 products by total quantity sold (sum of quantity in order_items).",
        "hint": "JOIN order_items with products, SUM(quantity), ORDER BY DESC, LIMIT 5.",
        "solution": "SELECT p.name, SUM(oi.quantity) as total_sold FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY p.id, p.name ORDER BY total_sold DESC LIMIT 5"
    },
    # --- SUBQUERIES ---
    {
        "id": 40, "title": "Products Above Average Price",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find all products priced above the average product price.",
        "hint": "Use a subquery: WHERE price > (SELECT AVG(price) FROM products).",
        "solution": "SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)"
    },
    {
        "id": 41, "title": "Most Expensive Product",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find the product(s) with the maximum price using a subquery.",
        "hint": "WHERE price = (SELECT MAX(price) FROM products).",
        "solution": "SELECT * FROM products WHERE price = (SELECT MAX(price) FROM products)"
    },
    {
        "id": 42, "title": "Customers Who Ordered Product 1",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find all customers who ordered product with <code>id = 1</code>.",
        "hint": "Use a subquery to find customer_ids from orders and order_items.",
        "solution": "SELECT * FROM customers WHERE id IN (SELECT o.customer_id FROM orders o JOIN order_items oi ON o.id = oi.order_id WHERE oi.product_id = 1)"
    },
    {
        "id": 43, "title": "Orders Above Average Amount",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find all orders where <code>total_amount</code> is above the average order amount.",
        "hint": "WHERE total_amount > (SELECT AVG(total_amount) FROM orders).",
        "solution": "SELECT * FROM orders WHERE total_amount > (SELECT AVG(total_amount) FROM orders)"
    },
    {
        "id": 44, "title": "Customers With Maximum Orders",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find the customer(s) who have placed the most orders.",
        "hint": "Use a subquery to find the max order count per customer.",
        "solution": "SELECT customer_id, COUNT(*) as cnt FROM orders GROUP BY customer_id HAVING COUNT(*) = (SELECT MAX(c2) FROM (SELECT COUNT(*) as c2 FROM orders GROUP BY customer_id))"
    },
    {
        "id": 45, "title": "Products In Best Category",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find all products belonging to the category with the most products.",
        "hint": "Subquery to find category_id with MAX count.",
        "solution": "SELECT * FROM products WHERE category_id = (SELECT category_id FROM products GROUP BY category_id ORDER BY COUNT(*) DESC LIMIT 1)"
    },
    {
        "id": 46, "title": "Second Most Expensive Product",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find the product(s) with the second highest price.",
        "hint": "Use a subquery to exclude the maximum price, then find the MAX of the rest.",
        "solution": "SELECT * FROM products WHERE price = (SELECT MAX(price) FROM products WHERE price < (SELECT MAX(price) FROM products))"
    },
    {
        "id": 47, "title": "Customers Who Spent Above Average",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find customer_ids who have spent above the average total order amount per customer.",
        "hint": "Subquery for average spending, then filter customers above it.",
        "solution": "SELECT customer_id, SUM(total_amount) as total FROM orders GROUP BY customer_id HAVING SUM(total_amount) > (SELECT AVG(total_per_customer) FROM (SELECT SUM(total_amount) as total_per_customer FROM orders GROUP BY customer_id))"
    },
    {
        "id": 48, "title": "Uncategorized Products Check",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find products whose <code>category_id</code> does not exist in the categories table.",
        "hint": "Use NOT IN with a subquery on categories.",
        "solution": "SELECT * FROM products WHERE category_id NOT IN (SELECT id FROM categories)"
    },
    {
        "id": 49, "title": "Orders With All Products Expensive",
        "difficulty": "Advanced", "category": "Subqueries",
        "description": "Find order IDs where every product in that order has a unit_price > 30.",
        "hint": "Use NOT EXISTS or check that MIN(unit_price) > 30 per order.",
        "solution": "SELECT order_id FROM order_items GROUP BY order_id HAVING MIN(unit_price) > 30"
    },
    # --- STRING FUNCTIONS ---
    {
        "id": 50, "title": "Customer Full Names",
        "difficulty": "Intermediate", "category": "String Functions",
        "description": "Return a single <code>full_name</code> column combining first and last name with a space.",
        "hint": "Use || to concatenate in SQLite: first_name || ' ' || last_name.",
        "solution": "SELECT first_name || ' ' || last_name as full_name FROM customers"
    },
    {
        "id": 51, "title": "Uppercase Product Names",
        "difficulty": "Intermediate", "category": "String Functions",
        "description": "Return all product names in uppercase.",
        "hint": "Use UPPER(name).",
        "solution": "SELECT UPPER(name) as name FROM products"
    },
    {
        "id": 52, "title": "Products Starting With A",
        "difficulty": "Intermediate", "category": "String Functions",
        "description": "Find all products whose <code>name</code> starts with the letter 'A'.",
        "hint": "Use LIKE 'A%'.",
        "solution": "SELECT * FROM products WHERE name LIKE 'A%'"
    },
    {
        "id": 53, "title": "Customers With Gmail",
        "difficulty": "Intermediate", "category": "String Functions",
        "description": "Find all customers whose email ends with '@gmail.com'.",
        "hint": "Use LIKE '%@gmail.com'.",
        "solution": "SELECT * FROM customers WHERE email LIKE '%@gmail.com'"
    },
    {
        "id": 54, "title": "Product Name Length",
        "difficulty": "Intermediate", "category": "String Functions",
        "description": "Return the product name and the length of the name as <code>name_length</code>.",
        "hint": "Use LENGTH(name).",
        "solution": "SELECT name, LENGTH(name) as name_length FROM products"
    },
    # --- DATE FUNCTIONS ---
    {
        "id": 55, "title": "Orders This Year",
        "difficulty": "Intermediate", "category": "Date Functions",
        "description": "Find all orders placed in the year 2024.",
        "hint": "Use strftime('%Y', order_date) = '2024'.",
        "solution": "SELECT * FROM orders WHERE strftime('%Y', order_date) = '2024'"
    },
    {
        "id": 56, "title": "Order Year and Month",
        "difficulty": "Intermediate", "category": "Date Functions",
        "description": "List each order's <code>id</code> with its year and month extracted from <code>order_date</code>.",
        "hint": "Use strftime('%Y', order_date) and strftime('%m', order_date).",
        "solution": "SELECT id, strftime('%Y', order_date) as year, strftime('%m', order_date) as month FROM orders"
    },
    {
        "id": 57, "title": "Orders Per Month",
        "difficulty": "Intermediate", "category": "Date Functions",
        "description": "Count the number of orders per month (use format YYYY-MM).",
        "hint": "GROUP BY strftime('%Y-%m', order_date).",
        "solution": "SELECT strftime('%Y-%m', order_date) as month, COUNT(*) as order_count FROM orders GROUP BY strftime('%Y-%m', order_date)"
    },
    {
        "id": 58, "title": "Recent Orders (Last 90 Days)",
        "difficulty": "Intermediate", "category": "Date Functions",
        "description": "Find orders placed within the last 90 days from today.",
        "hint": "Use date('now', '-90 days').",
        "solution": "SELECT * FROM orders WHERE order_date >= date('now', '-90 days')"
    },
    {
        "id": 59, "title": "Monthly Revenue",
        "difficulty": "Intermediate", "category": "Date Functions",
        "description": "Find total revenue per month (YYYY-MM format) from the orders table.",
        "hint": "SUM(total_amount) GROUP BY strftime('%Y-%m', order_date).",
        "solution": "SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as revenue FROM orders GROUP BY strftime('%Y-%m', order_date)"
    },
    # --- CASE / CONDITIONAL ---
    {
        "id": 60, "title": "Price Category Label",
        "difficulty": "Intermediate", "category": "CASE",
        "description": "Label products as 'Budget' (price < 20), 'Mid-Range' (20-100), or 'Premium' (> 100).",
        "hint": "Use a CASE WHEN ... THEN ... ELSE ... END expression.",
        "solution": "SELECT name, price, CASE WHEN price < 20 THEN 'Budget' WHEN price <= 100 THEN 'Mid-Range' ELSE 'Premium' END as price_category FROM products"
    },
    {
        "id": 61, "title": "Order Status Label",
        "difficulty": "Intermediate", "category": "CASE",
        "description": "For each order, add a column <code>is_complete</code> that is 1 if status='Delivered' else 0.",
        "hint": "Use CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END.",
        "solution": "SELECT *, CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END as is_complete FROM orders"
    },
    {
        "id": 62, "title": "Stock Status",
        "difficulty": "Intermediate", "category": "CASE",
        "description": "Label products as 'Out of Stock' if stock=0, 'Low Stock' if stock <= 10, else 'In Stock'.",
        "hint": "Use nested CASE WHEN conditions.",
        "solution": "SELECT name, stock, CASE WHEN stock = 0 THEN 'Out of Stock' WHEN stock <= 10 THEN 'Low Stock' ELSE 'In Stock' END as stock_status FROM products"
    },
    {
        "id": 63, "title": "Count By Price Tier",
        "difficulty": "Intermediate", "category": "CASE",
        "description": "Count how many products fall into each price tier (Budget/Mid-Range/Premium).",
        "hint": "Wrap the CASE inside COUNT in a GROUP BY.",
        "solution": "SELECT CASE WHEN price < 20 THEN 'Budget' WHEN price <= 100 THEN 'Mid-Range' ELSE 'Premium' END as tier, COUNT(*) as cnt FROM products GROUP BY tier"
    },
    {
        "id": 64, "title": "Conditional Revenue",
        "difficulty": "Advanced", "category": "CASE",
        "description": "Calculate two totals: revenue from Shipped orders and revenue from Delivered orders in one query.",
        "hint": "Use SUM(CASE WHEN status='Shipped' THEN total_amount ELSE 0 END).",
        "solution": "SELECT SUM(CASE WHEN status='Shipped' THEN total_amount ELSE 0 END) as shipped_revenue, SUM(CASE WHEN status='Delivered' THEN total_amount ELSE 0 END) as delivered_revenue FROM orders"
    },
    # --- WINDOW FUNCTIONS (SQLite 3.25+) ---
    {
        "id": 65, "title": "Row Number by Price",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "Assign a row number to each product ordered by price descending.",
        "hint": "Use ROW_NUMBER() OVER (ORDER BY price DESC).",
        "solution": "SELECT name, price, ROW_NUMBER() OVER (ORDER BY price DESC) as rank FROM products"
    },
    {
        "id": 66, "title": "Running Total of Orders",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "Compute a running total of <code>total_amount</code> over orders sorted by <code>order_date</code>.",
        "hint": "Use SUM(total_amount) OVER (ORDER BY order_date).",
        "solution": "SELECT id, order_date, total_amount, SUM(total_amount) OVER (ORDER BY order_date) as running_total FROM orders"
    },
    {
        "id": 67, "title": "Rank Products Within Category",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "Rank products by price within each category (highest price = rank 1).",
        "hint": "RANK() OVER (PARTITION BY category_id ORDER BY price DESC).",
        "solution": "SELECT name, category_id, price, RANK() OVER (PARTITION BY category_id ORDER BY price DESC) as price_rank FROM products"
    },
    {
        "id": 68, "title": "Lead: Next Order Date",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "For each order per customer, show the next order date using LEAD.",
        "hint": "LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date).",
        "solution": "SELECT id, customer_id, order_date, LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as next_order_date FROM orders"
    },
    {
        "id": 69, "title": "Lag: Previous Order Amount",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "For each order per customer, show the previous order's <code>total_amount</code> using LAG.",
        "hint": "LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date).",
        "solution": "SELECT id, customer_id, order_date, total_amount, LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) as prev_amount FROM orders"
    },
    # --- CTEs ---
    {
        "id": 70, "title": "CTE: Customer Totals",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Use a CTE to first compute total spending per customer, then select customers who spent over $300.",
        "hint": "WITH cte AS (SELECT customer_id, SUM(...) ...) SELECT ... FROM cte WHERE ...",
        "solution": "WITH customer_totals AS (SELECT customer_id, SUM(total_amount) as total FROM orders GROUP BY customer_id) SELECT * FROM customer_totals WHERE total > 300"
    },
    {
        "id": 71, "title": "CTE: Top Products",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Use a CTE to calculate total quantity sold per product, then return the top 3.",
        "hint": "WITH sales AS (...) SELECT ... FROM sales ORDER BY ... LIMIT 3.",
        "solution": "WITH product_sales AS (SELECT product_id, SUM(quantity) as total_sold FROM order_items GROUP BY product_id) SELECT p.name, ps.total_sold FROM product_sales ps JOIN products p ON ps.product_id = p.id ORDER BY ps.total_sold DESC LIMIT 3"
    },
    {
        "id": 72, "title": "CTE: Average Order Value",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Use a CTE to compute the average order amount, then list all orders above that average.",
        "hint": "WITH avg_cte AS (SELECT AVG(total_amount) as avg_val FROM orders) SELECT ... FROM orders, avg_cte WHERE ...",
        "solution": "WITH avg_cte AS (SELECT AVG(total_amount) as avg_val FROM orders) SELECT o.* FROM orders o, avg_cte WHERE o.total_amount > avg_cte.avg_val"
    },
    {
        "id": 73, "title": "CTE: Category Revenue Rank",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Use a CTE to calculate revenue per category, then rank categories by revenue.",
        "hint": "CTE for revenue, then use RANK() OVER (ORDER BY revenue DESC) on it.",
        "solution": "WITH cat_rev AS (SELECT cat.name, SUM(oi.unit_price * oi.quantity) as revenue FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN categories cat ON p.category_id = cat.id GROUP BY cat.id, cat.name) SELECT name, revenue, RANK() OVER (ORDER BY revenue DESC) as revenue_rank FROM cat_rev"
    },
    {
        "id": 74, "title": "CTE: Monthly Growth",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Use a CTE to get monthly revenue, then use LAG to show the previous month's revenue alongside each month.",
        "hint": "CTE for monthly revenue, then LAG(revenue) OVER (ORDER BY month).",
        "solution": "WITH monthly AS (SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as revenue FROM orders GROUP BY month) SELECT month, revenue, LAG(revenue) OVER (ORDER BY month) as prev_revenue FROM monthly"
    },
    # --- MISC / ADVANCED ---
    {
        "id": 75, "title": "UNION: All Names",
        "difficulty": "Advanced", "category": "Set Operations",
        "description": "Return a combined list of all customer first names and all product names as a single <code>name</code> column.",
        "hint": "Use UNION ALL between two SELECT statements.",
        "solution": "SELECT first_name as name FROM customers UNION ALL SELECT name FROM products"
    },
    {
        "id": 76, "title": "INTERSECT: Shared Names",
        "difficulty": "Advanced", "category": "Set Operations",
        "description": "Find first names that appear both in <code>customers</code> and as product <code>name</code>s.",
        "hint": "Use INTERSECT between two SELECT statements.",
        "solution": "SELECT first_name as name FROM customers INTERSECT SELECT name FROM products"
    },
    {
        "id": 77, "title": "EXCEPT: Customers Not Ordering",
        "difficulty": "Advanced", "category": "Set Operations",
        "description": "Find customer IDs from the customers table that do NOT appear in the orders table.",
        "hint": "SELECT id FROM customers EXCEPT SELECT customer_id FROM orders.",
        "solution": "SELECT id FROM customers EXCEPT SELECT customer_id FROM orders"
    },
    {
        "id": 78, "title": "Self Join: Same City Customers",
        "difficulty": "Advanced", "category": "Self Join",
        "description": "Find pairs of customers who live in the same <code>city</code> (exclude same-person pairs).",
        "hint": "JOIN customers c1 with customers c2 ON c1.city = c2.city AND c1.id < c2.id.",
        "solution": "SELECT c1.first_name, c1.last_name, c2.first_name as other_first, c2.last_name as other_last, c1.city FROM customers c1 JOIN customers c2 ON c1.city = c2.city AND c1.id < c2.id"
    },
    {
        "id": 79, "title": "CROSS JOIN: Product-Category Matrix",
        "difficulty": "Advanced", "category": "Self Join",
        "description": "Generate a row for every combination of product name and category name using CROSS JOIN.",
        "hint": "SELECT p.name, cat.name FROM products p CROSS JOIN categories cat.",
        "solution": "SELECT p.name as product, cat.name as category FROM products p CROSS JOIN categories cat"
    },
    {
        "id": 80, "title": "EXISTS: Customers With Orders",
        "difficulty": "Advanced", "category": "EXISTS",
        "description": "Find all customers for whom at least one order exists.",
        "hint": "Use WHERE EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id).",
        "solution": "SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)"
    },
    {
        "id": 81, "title": "NOT EXISTS: Products Not Sold",
        "difficulty": "Advanced", "category": "EXISTS",
        "description": "Find products that have never been sold (no entry in order_items).",
        "hint": "WHERE NOT EXISTS (SELECT 1 FROM order_items WHERE product_id = products.id).",
        "solution": "SELECT * FROM products p WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.id)"
    },
    {
        "id": 82, "title": "COALESCE: Default City",
        "difficulty": "Intermediate", "category": "NULL Handling",
        "description": "Return each customer's name and city, using 'Unknown' where city is NULL.",
        "hint": "Use COALESCE(city, 'Unknown').",
        "solution": "SELECT first_name, last_name, COALESCE(city, 'Unknown') as city FROM customers"
    },
    {
        "id": 83, "title": "NULLIF: Avoid Division by Zero",
        "difficulty": "Advanced", "category": "NULL Handling",
        "description": "Calculate average order value per customer; where a customer has 0 orders, return NULL instead of dividing by zero.",
        "hint": "Use NULLIF(COUNT(o.id), 0) as denominator.",
        "solution": "SELECT c.id, c.first_name, SUM(o.total_amount) / NULLIF(COUNT(o.id), 0) as avg_order FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.first_name"
    },
    {
        "id": 84, "title": "IS NULL: Customers Without City",
        "difficulty": "Beginner", "category": "NULL Handling",
        "description": "Find all customers where the <code>city</code> column is NULL.",
        "hint": "Use WHERE city IS NULL.",
        "solution": "SELECT * FROM customers WHERE city IS NULL"
    },
    {
        "id": 85, "title": "BETWEEN: Mid-Price Products",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Find all products with a price between 15 and 60 (inclusive).",
        "hint": "Use WHERE price BETWEEN 15 AND 60.",
        "solution": "SELECT * FROM products WHERE price BETWEEN 15 AND 60"
    },
    {
        "id": 86, "title": "IN: Specific Statuses",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Find all orders with status either 'Pending' or 'Processing'.",
        "hint": "Use WHERE status IN ('Pending', 'Processing').",
        "solution": "SELECT * FROM orders WHERE status IN ('Pending', 'Processing')"
    },
    {
        "id": 87, "title": "LIKE: Products Containing 'Pro'",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Find all products whose name contains the word 'Pro' (case-insensitive).",
        "hint": "Use WHERE name LIKE '%Pro%'.",
        "solution": "SELECT * FROM products WHERE name LIKE '%Pro%'"
    },
    {
        "id": 88, "title": "Limit and Offset: Page 2",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Return the second page of products (5 per page) ordered by id.",
        "hint": "Use LIMIT 5 OFFSET 5.",
        "solution": "SELECT * FROM products ORDER BY id LIMIT 5 OFFSET 5"
    },
    {
        "id": 89, "title": "Multiple Conditions: AND",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Find products priced above $50 AND with stock greater than 5.",
        "hint": "Use WHERE price > 50 AND stock > 5.",
        "solution": "SELECT * FROM products WHERE price > 50 AND stock > 5"
    },
    {
        "id": 90, "title": "Multiple Conditions: OR",
        "difficulty": "Beginner", "category": "Filtering",
        "description": "Find orders that are either 'Cancelled' or have a total_amount greater than 200.",
        "hint": "Use WHERE status = 'Cancelled' OR total_amount > 200.",
        "solution": "SELECT * FROM orders WHERE status = 'Cancelled' OR total_amount > 200"
    },
    {
        "id": 91, "title": "Count Distinct Customers Who Ordered",
        "difficulty": "Intermediate", "category": "Aggregates",
        "description": "Count the number of distinct customers who have placed at least one order.",
        "hint": "Use COUNT(DISTINCT customer_id) FROM orders.",
        "solution": "SELECT COUNT(DISTINCT customer_id) as unique_customers FROM orders"
    },
    {
        "id": 92, "title": "Average Items Per Order",
        "difficulty": "Intermediate", "category": "Aggregates",
        "description": "Calculate the average number of distinct items per order in the order_items table.",
        "hint": "Subquery to count items per order, then AVG of that.",
        "solution": "SELECT AVG(item_count) as avg_items FROM (SELECT order_id, COUNT(*) as item_count FROM order_items GROUP BY order_id)"
    },
    {
        "id": 93, "title": "Percentage of Total Revenue",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "For each order, show its total_amount and what percentage of overall revenue it represents.",
        "hint": "Use SUM(total_amount) OVER () to get the grand total.",
        "solution": "SELECT id, total_amount, ROUND(100.0 * total_amount / SUM(total_amount) OVER (), 2) as pct_of_total FROM orders"
    },
    {
        "id": 94, "title": "Cumulative Distinct Customers",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "For each order (ordered by date), show a running count of distinct customers seen so far. (Approximate using DENSE_RANK).",
        "hint": "DENSE_RANK() OVER (ORDER BY customer_id) gives a unique rank per customer.",
        "solution": "SELECT id, order_date, customer_id, DENSE_RANK() OVER (ORDER BY customer_id) as customer_rank FROM orders ORDER BY order_date"
    },
    {
        "id": 95, "title": "Product Price Percentile",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "Use NTILE to split products into 4 quartiles by price.",
        "hint": "NTILE(4) OVER (ORDER BY price).",
        "solution": "SELECT name, price, NTILE(4) OVER (ORDER BY price) as quartile FROM products"
    },
    {
        "id": 96, "title": "First Order Per Customer",
        "difficulty": "Advanced", "category": "Window Functions",
        "description": "Find the first order date for each customer using FIRST_VALUE.",
        "hint": "FIRST_VALUE(order_date) OVER (PARTITION BY customer_id ORDER BY order_date).",
        "solution": "SELECT DISTINCT customer_id, FIRST_VALUE(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as first_order_date FROM orders"
    },
    {
        "id": 97, "title": "Most Recent Order Per Customer",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "For each customer, return only their most recent order using a CTE and ROW_NUMBER.",
        "hint": "CTE with ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC), then filter WHERE rn = 1.",
        "solution": "WITH ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as rn FROM orders) SELECT * FROM ranked WHERE rn = 1"
    },
    {
        "id": 98, "title": "Customer Lifetime Value",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Calculate each customer's total lifetime spend, average order value, and number of orders in one query.",
        "hint": "JOIN customers with orders, GROUP BY customer, compute SUM, AVG, COUNT.",
        "solution": "SELECT c.id, c.first_name, c.last_name, COUNT(o.id) as num_orders, SUM(o.total_amount) as lifetime_value, AVG(o.total_amount) as avg_order_value FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.first_name, c.last_name"
    },
    {
        "id": 99, "title": "Sales Report",
        "difficulty": "Advanced", "category": "CTEs",
        "description": "Generate a full sales report: for each category, show total revenue, number of orders, and top product (by revenue). Use CTEs.",
        "hint": "Multiple CTEs: one for category revenue, one for top products. Join them together.",
        "solution": "WITH cat_rev AS (SELECT p.category_id, cat.name as cat_name, SUM(oi.unit_price * oi.quantity) as revenue, COUNT(DISTINCT oi.order_id) as num_orders FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN categories cat ON p.category_id = cat.id GROUP BY p.category_id, cat.name), top_products AS (SELECT p.category_id, p.name as top_product, SUM(oi.unit_price * oi.quantity) as prod_rev, ROW_NUMBER() OVER (PARTITION BY p.category_id ORDER BY SUM(oi.unit_price * oi.quantity) DESC) as rn FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY p.category_id, p.id, p.name) SELECT cr.cat_name, cr.revenue, cr.num_orders, tp.top_product FROM cat_rev cr JOIN top_products tp ON cr.category_id = tp.category_id AND tp.rn = 1 ORDER BY cr.revenue DESC"
    },
]


def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            city TEXT
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            stock INTEGER,
            category_id INTEGER REFERENCES categories(id)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            order_date TEXT,
            total_amount REAL,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            unit_price REAL
        );
    """)

    # Seed data if empty
    if cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        categories = [
            (1, "Electronics"), (2, "Clothing"), (3, "Books"),
            (4, "Home & Garden"), (5, "Sports"), (6, "Toys"),
        ]
        cur.executemany("INSERT INTO categories VALUES (?, ?)", categories)

        customers = [
            (1, "Alice", "Smith", "alice@example.com", "New York"),
            (2, "Bob", "Johnson", "bob@gmail.com", "Chicago"),
            (3, "Carol", "Williams", "carol@example.com", "New York"),
            (4, "David", "Brown", "david@gmail.com", None),
            (5, "Eve", "Jones", "eve@example.com", "Houston"),
            (6, "Frank", "Davis", "frank@gmail.com", "Chicago"),
            (7, "Grace", "Miller", "grace@example.com", "Phoenix"),
            (8, "Henry", "Wilson", "henry@gmail.com", "Houston"),
            (9, "Iris", "Moore", "iris@example.com", None),
            (10, "Jack", "Taylor", "jack@gmail.com", "Phoenix"),
            (11, "Karen", "Anderson", "karen@example.com", "Chicago"),
            (12, "Leo", "Thomas", "leo@gmail.com", "New York"),
            (13, "Mia", "Jackson", "mia@example.com", "Houston"),
            (14, "Nate", "White", "nate@gmail.com", "Chicago"),
            (15, "Olivia", "Harris", "olivia@example.com", "Phoenix"),
        ]
        cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

        products = [
            (1, "Laptop Pro", 999.99, 15, 1),
            (2, "Wireless Mouse", 29.99, 50, 1),
            (3, "USB-C Hub", 49.99, 30, 1),
            (4, "Monitor 4K", 349.99, 10, 1),
            (5, "Keyboard Mech", 89.99, 25, 1),
            (6, "Webcam HD", 79.99, 20, 1),
            (7, "Headphones Pro", 199.99, 18, 1),
            (8, "Running Shoes", 59.99, 40, 5),
            (9, "Yoga Mat", 24.99, 60, 5),
            (10, "Dumbbells Set", 79.99, 12, 5),
            (11, "Bicycle Helmet", 44.99, 30, 5),
            (12, "Water Bottle", 14.99, 100, 5),
            (13, "Python Basics", 19.99, 0, 3),
            (14, "SQL Mastery", 24.99, 5, 3),
            (15, "Data Science 101", 34.99, 8, 3),
            (16, "Clean Code", 29.99, 12, 3),
            (17, "Algorithms Book", 39.99, 7, 3),
            (18, "T-Shirt Cotton", 15.99, 200, 2),
            (19, "Jeans Slim Fit", 49.99, 80, 2),
            (20, "Hoodie Classic", 39.99, 60, 2),
            (21, "Jacket Winter", 89.99, 25, 2),
            (22, "Garden Hose", 34.99, 15, 4),
            (23, "Plant Pot Set", 22.99, 35, 4),
            (24, "Tool Kit", 54.99, 20, 4),
            (25, "LED Grow Light", 64.99, 10, 4),
            (26, "LEGO Set", 44.99, 30, 6),
            (27, "Board Game", 34.99, 40, 6),
            (28, "Puzzle 1000pc", 17.99, 50, 6),
            (29, "Action Figure", 12.99, 75, 6),
            (30, "Tablet Kids", 129.99, 0, 6),
        ]
        cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

        import random
        random.seed(42)
        statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        orders = []
        for i in range(1, 61):
            cust_id = random.randint(1, 15)
            day = random.randint(1, 28)
            month = random.randint(1, 12)
            year = random.choice([2023, 2024, 2024, 2024])
            date = f"{year}-{month:02d}-{day:02d}"
            amount = round(random.uniform(20, 600), 2)
            status = random.choice(statuses)
            orders.append((i, cust_id, date, amount, status))
        cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)

        order_items = []
        item_id = 1
        for order_id, _, _, _, _ in orders:
            num_items = random.randint(1, 4)
            used_products = random.sample(range(1, 31), num_items)
            for prod_id in used_products:
                qty = random.randint(1, 5)
                price = next(p[2] for p in products if p[0] == prod_id)
                order_items.append((item_id, order_id, prod_id, qty, price))
                item_id += 1
        cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", order_items)

        conn.commit()

    return conn


def run_query(conn, sql):
    try:
        df = pd.read_sql_query(sql, conn)
        return df, None
    except Exception as e:
        return None, str(e)


def normalize_df(df):
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df = df.applymap(lambda x: round(float(x), 4) if isinstance(x, float) else x)
    return df


def grade_query(conn, user_sql, solution_sql):
    user_df, user_err = run_query(conn, user_sql)
    if user_err:
        return {"status": "error", "message": f"SQL Error: {user_err}", "user_result": None, "expected_result": None}

    sol_df, sol_err = run_query(conn, solution_sql)
    if sol_err:
        return {"status": "error", "message": f"Internal error with solution.", "user_result": None, "expected_result": None}

    u = normalize_df(user_df)
    s = normalize_df(sol_df)

    u_sorted = u.sort_values(by=list(u.columns)).reset_index(drop=True)
    s_sorted = s.sort_values(by=list(s.columns)).reset_index(drop=True)

    if u_sorted.equals(s_sorted):
        correct = True
    elif set(u.columns) == set(s.columns) and u_sorted[sorted(u.columns)].equals(s_sorted[sorted(s.columns)]):
        correct = True
    else:
        correct = False

    return {
        "status": "correct" if correct else "incorrect",
        "message": "Correct! Well done." if correct else "Not quite — check your results against the expected output.",
        "user_result": user_df.to_dict(orient="split"),
        "expected_result": sol_df.to_dict(orient="split"),
        "row_match": len(user_df) == len(sol_df),
        "col_match": set(u.columns) == set(s.columns),
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        exercise_id = int(request.form.get('exercise_id', 0))
    except (ValueError, TypeError):
        exercise_id = 0

    user_query_text = request.form.get('query', '')
    feedback = {}
    conn = setup_db()

    if request.method == 'POST' and user_query_text:
        feedback = grade_query(conn, user_query_text, EXERCISES[exercise_id]['solution'])

    conn.close()
    return render_template('index.html',
                           exercises=EXERCISES,
                           selected_id=exercise_id,
                           exercise=EXERCISES[exercise_id],
                           feedback=feedback,
                           user_query=user_query_text)


@app.route('/api/run', methods=['POST'])
def api_run():
    data = request.get_json()
    exercise_id = int(data.get('exercise_id', 0))
    user_sql = data.get('query', '').strip()

    if not user_sql:
        return jsonify({"status": "error", "message": "No query provided."})

    conn = setup_db()
    result = grade_query(conn, user_sql, EXERCISES[exercise_id]['solution'])
    conn.close()
    return jsonify(result)


if __name__ == '__main__':
    setup_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
