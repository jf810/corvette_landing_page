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
    next_maintenance = db.execute("SELECT * FROM maintenance WHERE status = 'Pending' ORDER BY next_due_date LIMIT 1").fetchone()
    total_spent = db.execute("SELECT COALESCE(SUM(cost), 0) as total FROM repairs").fetchone()["total"]
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
    status_filter = request.args.get("status", "")
    sort = request.args.get("sort", "id")
    allowed_sorts = ["id", "cost", "start_date", "finish_date", "title"]
    if sort not in allowed_sorts:
        sort = "id"
    query = "SELECT * FROM repairs"
    params = []
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    query += f" ORDER BY {sort} DESC"
    rows = db.execute(query, params).fetchall()
    repairs = [dict(r) for r in rows]
    db.close()
    return render_template("repairs.html", repairs=repairs,
                           request_status=status_filter, request_sort=sort)

@app.route("/repairs/add", methods=["POST"])
def add_repair():
    db = get_db()
    db.execute(
        """INSERT INTO repairs
           (title, status, category, cost, start_date, start_date_unknown, finish_date, finish_date_unknown,
            time_taken, paid_for_service, mechanic, vendor, purchase_link, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (request.form["title"], request.form["status"],
         request.form.get("category") or None,
         request.form.get("cost") or 0,
         request.form.get("start_date") or None,
         1 if request.form.get("start_date_unknown") else 0,
         request.form.get("finish_date") or None,
         1 if request.form.get("finish_date_unknown") else 0,
         request.form.get("time_taken") or None,
         1 if request.form.get("paid_for_service") else 0,
         request.form.get("mechanic") or None,
         request.form.get("vendor") or None,
         request.form.get("purchase_link") or None,
         request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("repairs"))

@app.route("/repairs/edit/<int:repair_id>")
def edit_repair(repair_id):
    db = get_db()
    repairs = [dict(r) for r in db.execute("SELECT * FROM repairs ORDER BY id DESC").fetchall()]
    db.close()
    return render_template("repairs.html", repairs=repairs, edit=None,
                           request_status="", request_sort="id")

@app.route("/repairs/update/<int:repair_id>", methods=["POST"])
def update_repair(repair_id):
    db = get_db()
    db.execute(
        """UPDATE repairs SET title=?, status=?, category=?, cost=?, start_date=?, start_date_unknown=?,
           finish_date=?, finish_date_unknown=?, time_taken=?, paid_for_service=?, mechanic=?,
           vendor=?, purchase_link=?, notes=? WHERE id=?""",
        (request.form["title"], request.form["status"],
         request.form.get("category") or None,
         request.form.get("cost") or 0,
         request.form.get("start_date") or None,
         1 if request.form.get("start_date_unknown") else 0,
         request.form.get("finish_date") or None,
         1 if request.form.get("finish_date_unknown") else 0,
         request.form.get("time_taken") or None,
         1 if request.form.get("paid_for_service") else 0,
         request.form.get("mechanic") or None,
         request.form.get("vendor") or None,
         request.form.get("purchase_link") or None,
         request.form.get("notes") or None,
         repair_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("repairs"))

@app.route("/repairs/delete/<int:repair_id>", methods=["POST"])
def delete_repair(repair_id):
    db = get_db()
    db.execute("DELETE FROM repairs WHERE id = ?", (repair_id,))
    db.commit()
    db.close()
    return redirect(url_for("repairs"))

@app.route("/specs")
def specs():
    return render_template("specs.html")

@app.route("/maintenance")
def maintenance():
    from datetime import datetime, timedelta
    db = get_db()
    status_filter = request.args.get("status", "")
    recurring_filter = request.args.get("recurring", "")
    sort = request.args.get("sort", "next_due_date")

    query = "SELECT * FROM maintenance"
    params = []
    conditions = []
    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)
    if recurring_filter:
        conditions.append("recurring = ?")
        params.append(1 if recurring_filter == "1" else 0)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY {sort}"

    tasks = [dict(t) for t in db.execute(query, params).fetchall()]
    db.close()
    return render_template("maintenance.html", tasks=tasks,
                           request_status=status_filter,
                           request_recurring=recurring_filter,
                           request_sort=sort)

def compute_next_due(finish_date_str, months_min):
    import calendar
    from datetime import date
    try:
        y, m, d = [int(x) for x in finish_date_str.split("-")]
        m += int(months_min)
        y += (m - 1) // 12
        m = (m - 1) % 12 + 1
        d = min(d, calendar.monthrange(y, m)[1])
        return date(y, m, d).strftime("%Y-%m-%d")
    except Exception:
        return None

@app.route("/maintenance/add", methods=["POST"])
def add_maintenance():
    db = get_db()
    recurring = 1 if request.form.get("recurring") else 0
    finish_date = request.form.get("finish_date") or None
    months_min = request.form.get("frequency_months_min") or None
    next_due = None
    if recurring and finish_date and months_min:
        next_due = compute_next_due(finish_date, int(months_min))
    db.execute(
        """INSERT INTO maintenance
           (task, status, start_date, start_date_unknown, finish_date, finish_date_unknown,
            time_taken, paid_for_service, mechanic, vendor, purchase_link, recurring,
            frequency_miles, frequency_months_min, frequency_months_max, next_due_date, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (request.form["task"], request.form["status"],
         request.form.get("start_date") or None,
         1 if request.form.get("start_date_unknown") else 0,
         finish_date,
         1 if request.form.get("finish_date_unknown") else 0,
         request.form.get("time_taken") or None,
         1 if request.form.get("paid_for_service") else 0,
         request.form.get("mechanic") or None,
         request.form.get("vendor") or None,
         request.form.get("purchase_link") or None,
         recurring,
         request.form.get("frequency_miles") or None,
         months_min,
         request.form.get("frequency_months_max") or None,
         next_due,
         request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("maintenance"))

@app.route("/maintenance/update/<int:task_id>", methods=["POST"])
def update_maintenance(task_id):
    db = get_db()
    recurring = 1 if request.form.get("recurring") else 0
    finish_date = request.form.get("finish_date") or None
    months_min = request.form.get("frequency_months_min") or None
    next_due = None
    if recurring and finish_date and months_min:
        next_due = compute_next_due(finish_date, int(months_min))
    db.execute(
        """UPDATE maintenance SET task=?, status=?, start_date=?, start_date_unknown=?,
           finish_date=?, finish_date_unknown=?, time_taken=?, paid_for_service=?, mechanic=?,
           vendor=?, purchase_link=?, recurring=?, frequency_miles=?, frequency_months_min=?,
           frequency_months_max=?, next_due_date=?, notes=? WHERE id=?""",
        (request.form["task"], request.form["status"],
         request.form.get("start_date") or None,
         1 if request.form.get("start_date_unknown") else 0,
         finish_date,
         1 if request.form.get("finish_date_unknown") else 0,
         request.form.get("time_taken") or None,
         1 if request.form.get("paid_for_service") else 0,
         request.form.get("mechanic") or None,
         request.form.get("vendor") or None,
         request.form.get("purchase_link") or None,
         recurring,
         request.form.get("frequency_miles") or None,
         months_min,
         request.form.get("frequency_months_max") or None,
         next_due,
         request.form.get("notes") or None,
         task_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("maintenance"))

@app.route("/maintenance/delete/<int:task_id>", methods=["POST"])
def delete_maintenance(task_id):
    db = get_db()
    db.execute("DELETE FROM maintenance WHERE id = ?", (task_id,))
    db.commit()
    db.close()
    return redirect(url_for("maintenance"))

@app.route("/expenses")
def expenses():
    db = get_db()
    repairs = [dict(r) for r in db.execute(
        "SELECT title, cost, finish_date FROM repairs WHERE cost > 0 ORDER BY finish_date DESC"
    ).fetchall()]
    total = db.execute("SELECT COALESCE(SUM(cost), 0) as total FROM repairs WHERE cost > 0").fetchone()["total"]
    db.close()
    return render_template("expenses.html", repairs=repairs, total=total)

@app.route("/wishlist")
def wishlist():
    db = get_db()
    type_filter = request.args.get("type", "")
    category_filter = request.args.get("category", "")
    query = "SELECT * FROM wishlist"
    params = []
    conditions = []
    if type_filter:
        conditions.append("type = ?")
        params.append(type_filter)
    if category_filter:
        conditions.append("category = ?")
        params.append(category_filter)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY category, name"
    items = [dict(i) for i in db.execute(query, params).fetchall()]
    db.close()
    return render_template("wishlist.html", items=items,
                           request_type=type_filter,
                           request_category=category_filter)

@app.route("/wishlist/add", methods=["POST"])
def add_wishlist():
    db = get_db()
    db.execute(
        "INSERT INTO wishlist (name, type, category, estimated_price, link, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (request.form["name"],
         request.form.get("type") or "Repair/Upgrade",
         request.form.get("category") or None,
         request.form.get("estimated_price") or None,
         request.form.get("link") or None,
         request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("wishlist"))

@app.route("/wishlist/update/<int:item_id>", methods=["POST"])
def update_wishlist(item_id):
    db = get_db()
    db.execute(
        "UPDATE wishlist SET name=?, type=?, category=?, estimated_price=?, link=?, notes=? WHERE id=?",
        (request.form["name"],
         request.form.get("type") or "Repair/Upgrade",
         request.form.get("category") or None,
         request.form.get("estimated_price") or None,
         request.form.get("link") or None,
         request.form.get("notes") or None,
         item_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("wishlist"))

@app.route("/wishlist/delete/<int:item_id>", methods=["POST"])
def delete_wishlist(item_id):
    db = get_db()
    db.execute("DELETE FROM wishlist WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(url_for("wishlist"))

@app.route("/wishlist/promote/<int:item_id>", methods=["POST"])
def promote_wishlist(item_id):
    db = get_db()
    item = dict(db.execute("SELECT * FROM wishlist WHERE id = ?", (item_id,)).fetchone())
    db.execute(
        """INSERT INTO repairs (title, status, category, cost, purchase_link, notes)
           VALUES (?, 'Not Started', ?, ?, ?, ?)""",
        (item["name"], item.get("category"),
         item.get("estimated_price") or 0,
         item.get("link"), item.get("notes"))
    )
    db.execute("DELETE FROM wishlist WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(url_for("repairs"))

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
