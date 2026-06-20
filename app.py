from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "corvette.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    db = get_db()
    active_repairs = db.execute("SELECT * FROM repairs WHERE status != 'Done' LIMIT 3").fetchall()
    next_maintenance = db.execute("SELECT * FROM maintenance WHERE status = 'Pending' ORDER BY due_date LIMIT 1").fetchone()
    total_spent = db.execute("SELECT SUM(amount) as total FROM expenses").fetchone()["total"] or 0
    wishlist_count = db.execute("SELECT COUNT(*) as count FROM wishlist").fetchone()["count"]
    db.close()
    return render_template("dashboard.html",
        active_repairs=active_repairs,
        next_maintenance=next_maintenance,
        total_spent=total_spent,
        wishlist_count=wishlist_count)

@app.route("/repairs")
def repairs():
    db = get_db()
    repairs = db.execute("SELECT * FROM repairs ORDER BY id DESC").fetchall()
    db.close()
    return render_template("repairs.html", repairs=repairs)

@app.route("/repairs/add", methods=["POST"])
def add_repair():
    db = get_db()
    db.execute(
        "INSERT INTO repairs (title, status, cost, year, date, time_taken, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (request.form["title"], request.form["status"], request.form.get("cost") or 0,
         request.form.get("year") or None, request.form.get("date") or None,
         request.form.get("time_taken") or None, request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("repairs"))

@app.route("/specs")
def specs():
    db = get_db()
    specs = db.execute("SELECT * FROM specs ORDER BY field").fetchall()
    db.close()
    return render_template("specs.html", specs=specs)

@app.route("/specs/add", methods=["POST"])
def add_spec():
    db = get_db()
    db.execute(
        "INSERT INTO specs (field, value) VALUES (?, ?)",
        (request.form["field"], request.form["value"])
    )
    db.commit()
    db.close()
    return redirect(url_for("specs"))

@app.route("/maintenance")
def maintenance():
    db = get_db()
    tasks = db.execute("SELECT * FROM maintenance ORDER BY due_date").fetchall()
    db.close()
    return render_template("maintenance.html", tasks=tasks)

@app.route("/maintenance/add", methods=["POST"])
def add_maintenance():
    db = get_db()
    db.execute(
        "INSERT INTO maintenance (task, status, due_date, completed_date, time_taken, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (request.form["task"], request.form["status"],
         request.form.get("due_date") or None, request.form.get("completed_date") or None,
         request.form.get("time_taken") or None, request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("maintenance"))

@app.route("/expenses")
def expenses():
    db = get_db()
    expenses = db.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    total = db.execute("SELECT SUM(amount) as total FROM expenses").fetchone()["total"] or 0
    db.close()
    return render_template("expenses.html", expenses=expenses, total=total)

@app.route("/expenses/add", methods=["POST"])
def add_expense():
    db = get_db()
    db.execute(
        "INSERT INTO expenses (description, amount, date, category) VALUES (?, ?, ?, ?)",
        (request.form["description"], request.form["amount"],
         request.form.get("date") or None, request.form.get("category") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

@app.route("/wishlist")
def wishlist():
    db = get_db()
    items = db.execute("SELECT * FROM wishlist ORDER BY category, name").fetchall()
    db.close()
    return render_template("wishlist.html", items=items)

@app.route("/wishlist/add", methods=["POST"])
def add_wishlist():
    db = get_db()
    db.execute(
        "INSERT INTO wishlist (name, category, price, link, notes) VALUES (?, ?, ?, ?, ?)",
        (request.form["name"], request.form.get("category") or None,
         request.form.get("price") or None, request.form.get("link") or None,
         request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("wishlist"))

@app.route("/resources")
def resources():
    db = get_db()
    resources = db.execute("SELECT * FROM resources ORDER BY title").fetchall()
    db.close()
    return render_template("resources.html", resources=resources)

@app.route("/resources/add", methods=["POST"])
def add_resource():
    db = get_db()
    db.execute(
        "INSERT INTO resources (title, url, description) VALUES (?, ?, ?)",
        (request.form["title"], request.form["url"], request.form.get("description") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("resources"))

@app.route("/notes")
def notes():
    db = get_db()
    notes = db.execute("SELECT * FROM notes ORDER BY folder, created_at DESC").fetchall()
    db.close()
    return render_template("notes.html", notes=notes)

@app.route("/notes/add", methods=["POST"])
def add_note():
    db = get_db()
    db.execute(
        "INSERT INTO notes (title, folder, content) VALUES (?, ?, ?)",
        (request.form["title"], request.form.get("folder") or "General",
         request.form.get("content") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("notes"))

if __name__ == "__main__":
    app.run(debug=True)
