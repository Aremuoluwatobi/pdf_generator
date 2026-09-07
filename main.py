import sqlite3
from datetime import date
from fastapi import FastAPI
from fastapi.responses import FileResponse
from conn import get_report_data, get_all_books, build_html, render_pdf

app = FastAPI()

# create the reports table once, when the server starts
with sqlite3.connect("report.db") as connection:
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS reports(
            ID INTEGER PRIMARY KEY UNIQUE,
            path TEXT,
            created_at TEXT
            )"""
    )
    connection.commit()


@app.get("/health")
def check_health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
def create_report():
    report = get_report_data()
    my_books = get_all_books()
    html = build_html(report, my_books)

    with sqlite3.connect("report.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO reports (path, created_at) VALUES (?, ?)",
            ("", str(date.today()))
        )
        report_id = cursor.lastrowid

        file_path = f"reports/{report_id}.pdf"
        cursor.execute(
            "UPDATE reports SET path = ? WHERE ID = ?",
            (file_path, report_id)
        )
        connection.commit()

    render_pdf(html, output_path=file_path)

    return {"id": report_id, "file": f"/reports/{report_id}/file"}


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    with sqlite3.connect("report.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT ID, path, created_at FROM reports WHERE ID = ?", (report_id,))
        row = cursor.fetchone()

    if row is None:
        return {"error": "not found"}, 404

    return {"id": row[0], "path": row[1], "created_at": row[2], "file": f"/reports/{row[0]}/file"}


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    with sqlite3.connect("report.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT path FROM reports WHERE ID = ?", (report_id,))
        row = cursor.fetchone()

    if row is None:
        return {"error": "not found"}, 404

    return FileResponse(row[0], media_type="application/pdf")
