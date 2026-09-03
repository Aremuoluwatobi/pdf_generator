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

    cursor.execute("SELECT COUNT(*) FROM books")
    all_books = cursor.fetchall()
    print(all_books)
    connection.commit()
