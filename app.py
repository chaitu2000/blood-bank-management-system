from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).resolve().parent / "blood_bank.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(
        '''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            phone TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_group TEXT NOT NULL,
            units INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            units_needed INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        );
        '''
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_conn()
    donor_count = conn.execute("SELECT COUNT(*) AS c FROM donors").fetchone()["c"]
    request_count = conn.execute("SELECT COUNT(*) AS c FROM requests").fetchone()["c"]
    inventory_rows = conn.execute("SELECT blood_group, units FROM inventory ORDER BY blood_group").fetchall()
    conn.close()
    return render_template(
        "index.html",
        donor_count=donor_count,
        request_count=request_count,
        inventory_rows=inventory_rows,
    )


@app.route("/donors", methods=["GET", "POST"])
def donors():
    conn = get_conn()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO donors (name, blood_group, phone) VALUES (?, ?, ?)",
            (request.form["name"], request.form["blood_group"], request.form["phone"])
        )
        conn.commit()
        return redirect(url_for("donors"))

    rows = conn.execute("SELECT * FROM donors ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("donors.html", donors=rows)


@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    conn = get_conn()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO inventory (blood_group, units) VALUES (?, ?)",
            (request.form["blood_group"], int(request.form["units"]))
        )
        conn.commit()
        return redirect(url_for("inventory"))

    rows = conn.execute("SELECT * FROM inventory ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("inventory.html", inventory=rows)


@app.route("/requests", methods=["GET", "POST"])
def requests_page():
    conn = get_conn()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO requests (hospital_name, blood_group, units_needed) VALUES (?, ?, ?)",
            (
                request.form["hospital_name"],
                request.form["blood_group"],
                int(request.form["units_needed"]),
            )
        )
        conn.commit()
        return redirect(url_for("requests_page"))

    rows = conn.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("requests.html", requests=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
