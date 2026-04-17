from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    filter_type = request.args.get("filter", "today")

    if request.method == "POST":
        activity = request.form["activity"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            "INSERT INTO activities (name, timestamp) VALUES (?, ?)",
            (activity, timestamp)
        )
        conn.commit()

        return redirect(f"/?filter={filter_type}")

    if filter_type == "all":
        c.execute("SELECT * FROM activities ORDER BY timestamp DESC")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("""
            SELECT * FROM activities
            WHERE date(timestamp) = ?
            ORDER BY timestamp DESC
        """, (today,))

    activities = c.fetchall()
    conn.close()

    return render_template(
        "index.html",
        activities=activities,
        filter_type=filter_type
    )

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    filter_type = request.args.get("filter", "today")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM activities WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(f"/?filter={filter_type}")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    filter_type = request.args.get("filter", "today")

    if request.method == "POST":
        updated_activity = request.form["activity"]

        c.execute(
            "UPDATE activities SET name = ? WHERE id = ?",
            (updated_activity, id)
        )
        conn.commit()
        conn.close()

        return redirect(f"/?filter={filter_type}")

    c.execute("SELECT * FROM activities WHERE id = ?", (id,))
    activity = c.fetchone()
    conn.close()

    return render_template("edit.html", activity=activity, filter_type=filter_type)

if __name__ == "__main__":
    init_db()
    app.run()