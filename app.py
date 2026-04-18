from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"


def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Activities table
    c.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            timestamp TEXT,
            user_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    filter_type = request.args.get("filter", "today")

    if request.method == "POST":
        activity = request.form["activity"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute(
            "INSERT INTO activities (name, timestamp, user_id) VALUES (?, ?, ?)",
            (activity, timestamp, session["user_id"])
        )
        conn.commit()
        return redirect(f"/?filter={filter_type}")

    if filter_type == "all":
        c.execute(
            "SELECT * FROM activities WHERE user_id = ? ORDER BY timestamp DESC",
            (session["user_id"],)
        )
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("""
            SELECT * FROM activities
            WHERE user_id = ? AND date(timestamp) = ?
            ORDER BY timestamp DESC
        """, (session["user_id"], today))

    activities = c.fetchall()
    conn.close()

    return render_template(
        "index.html",
        activities=activities,
        filter_type=filter_type
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    filter_type = request.args.get("filter", "today")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "DELETE FROM activities WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect(f"/?filter={filter_type}")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    filter_type = request.args.get("filter", "today")

    if request.method == "POST":
        updated_activity = request.form["activity"]

        c.execute(
            "UPDATE activities SET name = ? WHERE id = ? AND user_id = ?",
            (updated_activity, id, session["user_id"])
        )
        conn.commit()
        conn.close()

        return redirect(f"/?filter={filter_type}")

    c.execute(
        "SELECT * FROM activities WHERE id = ? AND user_id = ?",
        (id, session["user_id"])
    )
    activity = c.fetchone()
    conn.close()

    return render_template("edit.html", activity=activity, filter_type=filter_type)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            conn.close()
            return "Username already exists"

    conn.close()
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        c.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = c.fetchone()

        if user:
            session["user_id"] = user[0]
            conn.close()
            return redirect("/")
        else:
            conn.close()
            return "Invalid credentials"

    conn.close()
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


if __name__ == "__main__":
    init_db()
    app.run()