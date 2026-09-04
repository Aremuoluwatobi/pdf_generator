import sqlite3
import json
from datetime import date
from playwright.sync_api import sync_playwright
import os
os.makedirs("reports", exist_ok=True)


with sqlite3.connect("report.db") as connection:
    cursor = connection.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS books(
            ID INTEGER PRIMARY KEY UNIQUE,
            title TEXT,
            price INT,
            rating INT,
            url TEXT
            )"""
    )

    cursor.execute(
        "DELETE FROM books")

    with open("books.json") as f:
        data = json.load(f)

        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        for book in data:
            cursor.execute("INSERT INTO books(title, price, rating, url) VALUES (?, ?, ?, ?)",
                           (book["title"], book["price_gbp"],
                            rating_map[book["rating_text"]], book["product_url"])
                           )

    connection.commit()


def get_report_data():
    with sqlite3.connect("report.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(price) FROM books")
        avg = cursor.fetchone()[0]
        cursor.execute(
            "SELECT title, price FROM books ORDER BY price DESC LIMIT 5;")
        cost_books = cursor.fetchall()
        cursor.execute(
            "SELECT rating, COUNT(*) FROM books GROUP BY rating")
        rating = cursor.fetchall()

        return {
            "total_count": total_count,
            "average_price": avg,
            "top_5_expensive": cost_books,
            "by_rating": rating
        }


def get_all_books():
    with sqlite3.connect("report.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM books")
        return cursor.fetchall()


def build_html(report, all_books):
    top_5_rows = ""
    for title, price in report["top_5_expensive"]:
        top_5_rows += f"<tr><td>{title}</td><td>£{price}</td></tr>"

    rating_rows = ""
    for rating, count in report["by_rating"]:
        rating_rows += f"<tr><td>{rating}</td><td>{count}</td></tr>"

    all_books_rows = ""
    for book_id, title, price, rating, url in all_books:
        all_books_rows += f"<tr><td>{title}</td><td>£{price}</td><td>{rating}</td></tr>"

    html = f"""
    <html>
    <body>
        <h1>Book Report</h1>
        <p>Generated on {date.today()}</p>
        <p>Total books: {report["total_count"]}</p>
        <p>Average price: £{report["average_price"]:.2f}</p>

        <h2>Top 5 most expensive</h2>
        <table>
            <thead><tr><th>Title</th><th>Price</th></tr></thead>
            {top_5_rows}
        </table>

        <h2>Books per rating</h2>
        <table>
            <thead><tr><th>Rating</th><th>Count</th></tr></thead>
            {rating_rows}
        </table>

        <h2>All books</h2>
        <table>
            <thead><tr><th>Title</th><th>Price</th><th>Rating</th></tr></thead>
            {all_books_rows}
        </table>
    </body>
    </html>
    """
    return html


def render_pdf(html, output_path="reports/test.pdf"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()


report = get_report_data()
my_books = get_all_books()
builder = build_html(report, my_books)
render_pdf(builder)
