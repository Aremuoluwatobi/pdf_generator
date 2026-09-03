import sqlite3
import json

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

        print({
            "total_count": total_count,
            "average_price": avg,
            "top_5_expensive": cost_books,
            "by_rating": rating
        })


get_report_data()
