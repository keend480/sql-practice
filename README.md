# SQL Practice — 100 Exercises

An interactive SQL practice app built with Flask and SQLite. Write real SQL queries, get instant feedback, and level up from beginner to advanced.

![Python](https://img.shields.io/badge/python-3.11-blue) ![Flask](https://img.shields.io/badge/flask-3.0.3-lightgrey) ![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **100 exercises** across 10 categories: SELECT, WHERE, ORDER BY, Aggregates, GROUP BY, HAVING, JOINs, Subqueries, NULL handling, and String functions
- **3 difficulty levels**: Beginner, Intermediate, Advanced
- **Auto-grading** — compares your query results against the expected output
- **Hints & solutions** available on demand
- **Dark mode UI** built with Tailwind CSS
- Live SQLite database with seeded sample data (customers, products, orders)

## Getting Started

### Prerequisites
- Python 3.11+

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/sql-practice.git
cd sql-practice
pip install -r requirements.txt
python main.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

The SQLite database (`practice.db`) is auto-created and seeded on first run.

## Project Structure

```
sql-practice/
├── main.py              # Flask app + exercises + DB setup
├── requirements.txt
├── practice.db          # SQLite database (auto-generated)
├── templates/
│   └── index.html       # Tailwind CSS frontend
└── static/              # Static assets
```

## Database Schema

| Table         | Key Columns                                              |
|---------------|----------------------------------------------------------|
| `customers`   | id, first_name, last_name, email, city                  |
| `products`    | id, name, price, stock, category_id                     |
| `categories`  | id, name                                                 |
| `orders`      | id, customer_id, order_date, total_amount, status       |
| `order_items` | id, order_id, product_id, quantity, unit_price          |

## Deployment

This app is Replit-ready (includes `.replit` config). To deploy elsewhere, any platform that supports Python + Flask will work (Railway, Render, Fly.io, etc.).

## License

MIT
