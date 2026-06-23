from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "corvette.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            code TEXT UNIQUE,
            notes TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            title             TEXT NOT NULL,
            category          TEXT,
            cost              REAL DEFAULT 0,
            purchase_month    TEXT,
            vendor            TEXT,
            mechanic          TEXT,
            notes             TEXT,
            group_id          INTEGER REFERENCES groups(id),
            group_expense_num INTEGER
        )
    """)
    try:
        db.execute("ALTER TABLE repairs ADD COLUMN group_id INTEGER REFERENCES groups(id)")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE maintenance ADD COLUMN group_id INTEGER REFERENCES groups(id)")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE expenses ADD COLUMN repair_id INTEGER REFERENCES repairs(id)")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE expenses ADD COLUMN maintenance_id INTEGER REFERENCES maintenance(id)")
    except Exception:
        pass
    db.commit()
    db.close()

init_db()

def resolve_group_id(db, group_id_form, group_name_form, group_type):
    """If group_id_form is 'new', create the group and return its id. Otherwise pass through."""
    if group_id_form == "new":
        name = (group_name_form or "").strip() or "Unnamed Group"
        count = db.execute(
            "SELECT COUNT(*) AS c FROM groups WHERE type = ?", (group_type,)
        ).fetchone()["c"]
        code = f"{group_type}{count + 1}"
        cursor = db.execute(
            "INSERT INTO groups (name, type, code) VALUES (?, ?, ?)",
            (name, group_type, code)
        )
        return cursor.lastrowid
    return int(group_id_form) if group_id_form else None

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
    query = "SELECT r.*, g.code AS group_code FROM repairs r LEFT JOIN groups g ON r.group_id = g.id"
    params = []
    if status_filter:
        query += " WHERE r.status = ?"
        params.append(status_filter)
    query += f" ORDER BY r.{sort} DESC"
    rows = db.execute(query, params).fetchall()
    repairs = [dict(r) for r in rows]
    groups = [dict(g) for g in db.execute("SELECT * FROM groups ORDER BY type, id").fetchall()]
    db.close()
    return render_template("repairs.html", repairs=repairs, groups=groups,
                           request_status=status_filter, request_sort=sort)

@app.route("/repairs/add", methods=["POST"])
def add_repair():
    db = get_db()
    group_id = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"), "R")
    db.execute(
        """INSERT INTO repairs
           (title, status, category, cost, start_date, start_date_unknown, finish_date, finish_date_unknown,
            time_taken, paid_for_service, mechanic, vendor, purchase_link, notes, group_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
         group_id)
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
    current = db.execute("SELECT group_id FROM repairs WHERE id = ?", (repair_id,)).fetchone()
    new_group_id = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"), "R")
    if str(new_group_id or "") != str(current["group_id"] or ""):
        # Find expenses directly linked to this repair, ordered by current num
        linked = db.execute(
            "SELECT id FROM expenses WHERE repair_id = ? ORDER BY group_expense_num",
            (repair_id,)
        ).fetchall()
        if linked:
            if new_group_id:
                row = db.execute(
                    "SELECT COALESCE(MAX(group_expense_num), 0) AS m FROM expenses "
                    "WHERE group_id = ? AND (repair_id IS NULL OR repair_id != ?)",
                    (new_group_id, repair_id)
                ).fetchone()
                start_num = row["m"] + 1
            else:
                start_num = None
            for i, exp in enumerate(linked):
                db.execute(
                    "UPDATE expenses SET group_id = ?, group_expense_num = ? WHERE id = ?",
                    (new_group_id, (start_num + i) if start_num is not None else None, exp["id"])
                )
    db.execute(
        """UPDATE repairs SET title=?, status=?, category=?, cost=?, start_date=?, start_date_unknown=?,
           finish_date=?, finish_date_unknown=?, time_taken=?, paid_for_service=?, mechanic=?,
           vendor=?, purchase_link=?, notes=?, group_id=? WHERE id=?""",
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
         new_group_id,
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

    allowed_sorts = ["next_due_date", "finish_date", "task", "id"]
    if sort not in allowed_sorts:
        sort = "next_due_date"
    query = "SELECT t.*, g.code AS group_code FROM maintenance t LEFT JOIN groups g ON t.group_id = g.id"
    params = []
    conditions = []
    if status_filter:
        conditions.append("t.status = ?")
        params.append(status_filter)
    if recurring_filter:
        conditions.append("t.recurring = ?")
        params.append(1 if recurring_filter == "1" else 0)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY t.{sort}"

    tasks = [dict(t) for t in db.execute(query, params).fetchall()]
    groups = [dict(g) for g in db.execute("SELECT * FROM groups ORDER BY type, id").fetchall()]
    db.close()
    return render_template("maintenance.html", tasks=tasks, groups=groups,
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
    group_id = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"), "M")
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
            frequency_miles, frequency_months_min, frequency_months_max, next_due_date, notes, group_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
         group_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("maintenance"))

@app.route("/maintenance/update/<int:task_id>", methods=["POST"])
def update_maintenance(task_id):
    db = get_db()
    current = db.execute("SELECT group_id FROM maintenance WHERE id = ?", (task_id,)).fetchone()
    new_group_id = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"), "M")
    if str(new_group_id or "") != str(current["group_id"] or ""):
        linked = db.execute(
            "SELECT id FROM expenses WHERE maintenance_id = ? ORDER BY group_expense_num",
            (task_id,)
        ).fetchall()
        if linked:
            if new_group_id:
                row = db.execute(
                    "SELECT COALESCE(MAX(group_expense_num), 0) AS m FROM expenses "
                    "WHERE group_id = ? AND (maintenance_id IS NULL OR maintenance_id != ?)",
                    (new_group_id, task_id)
                ).fetchone()
                start_num = row["m"] + 1
            else:
                start_num = None
            for i, exp in enumerate(linked):
                db.execute(
                    "UPDATE expenses SET group_id = ?, group_expense_num = ? WHERE id = ?",
                    (new_group_id, (start_num + i) if start_num is not None else None, exp["id"])
                )
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
           frequency_months_max=?, next_due_date=?, notes=?, group_id=? WHERE id=?""",
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
         new_group_id,
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
    from datetime import date, datetime
    db = get_db()

    all_expenses = [dict(r) for r in db.execute("""
        SELECT e.*,
            g.code  AS group_code,  g.name AS group_name,  g.type AS group_type,
            r.title AS linked_repair_title,
            mnt.task AS linked_maint_task
        FROM expenses e
        LEFT JOIN groups     g   ON e.group_id      = g.id
        LEFT JOIN repairs    r   ON e.repair_id     = r.id
        LEFT JOIN maintenance mnt ON e.maintenance_id = mnt.id
        ORDER BY e.purchase_month DESC, e.id DESC
    """).fetchall()]

    for e in all_expenses:
        if e.get("purchase_month"):
            try:
                dt = datetime.strptime(e["purchase_month"], "%Y-%m")
                e["purchase_month_display"] = dt.strftime("%b %Y")
            except Exception:
                e["purchase_month_display"] = e["purchase_month"]
        else:
            e["purchase_month_display"] = None

    total = db.execute("SELECT COALESCE(SUM(cost), 0) AS t FROM expenses").fetchone()["t"]

    today = date.today()
    months = []
    for i in range(11, -1, -1):
        m, y = today.month - i, today.year
        while m <= 0:
            m += 12
            y -= 1
        months.append((f"{y:04d}-{m:02d}", datetime(y, m, 1).strftime("%b '%y")))

    month_totals_raw = {
        row["purchase_month"]: float(row["total"])
        for row in db.execute(
            "SELECT purchase_month, SUM(cost) AS total FROM expenses "
            "WHERE purchase_month IS NOT NULL GROUP BY purchase_month"
        ).fetchall()
    }
    bar_labels = [m[1] for m in months]
    bar_values = [month_totals_raw.get(m[0], 0.0) for m in months]

    cat_rows = db.execute("""
        SELECT category, SUM(cost) AS total FROM expenses
        WHERE cost > 0 AND category IS NOT NULL AND category != ''
        GROUP BY category ORDER BY total DESC
    """).fetchall()
    donut_labels = [r["category"] for r in cat_rows]
    donut_values = [float(r["total"]) for r in cat_rows]

    avg_per_month = avg_per_year = 0.0
    if total > 0:
        first = db.execute(
            "SELECT MIN(purchase_month) AS m FROM expenses WHERE purchase_month IS NOT NULL"
        ).fetchone()["m"]
        if first:
            fy, fm = int(first[:4]), int(first[5:7])
            num_months = max((today.year - fy) * 12 + (today.month - fm) + 1, 1)
            avg_per_month = total / num_months
            avg_per_year = avg_per_month * 12

    groups = [dict(g) for g in db.execute(
        "SELECT * FROM groups ORDER BY type, id"
    ).fetchall()]
    all_repairs = [dict(r) for r in db.execute(
        "SELECT id, title FROM repairs ORDER BY title"
    ).fetchall()]
    all_maintenance = [dict(t) for t in db.execute(
        "SELECT id, task FROM maintenance ORDER BY task"
    ).fetchall()]

    db.close()
    return render_template("expenses.html",
        expenses=all_expenses,
        total=total,
        bar_labels=bar_labels,
        bar_values=bar_values,
        donut_labels=donut_labels,
        donut_values=donut_values,
        avg_per_month=avg_per_month,
        avg_per_year=avg_per_year,
        groups=groups,
        all_repairs=all_repairs,
        all_maintenance=all_maintenance,
    )

@app.route("/expenses/add", methods=["POST"])
def add_expense():
    db = get_db()
    group_id = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"),
                                request.form.get("group_type", "R"))
    group_expense_num = None
    if group_id:
        row = db.execute(
            "SELECT COALESCE(MAX(group_expense_num), 0) AS m FROM expenses WHERE group_id = ?",
            (group_id,)
        ).fetchone()
        group_expense_num = row["m"] + 1
    repair_id     = request.form.get("repair_id") or None
    maintenance_id = request.form.get("maintenance_id") or None
    db.execute(
        """INSERT INTO expenses
           (title, category, cost, purchase_month, vendor, mechanic, notes,
            group_id, group_expense_num, repair_id, maintenance_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (request.form["title"],
         request.form.get("category") or None,
         request.form.get("cost") or 0,
         request.form.get("purchase_month") or None,
         request.form.get("vendor") or None,
         request.form.get("mechanic") or None,
         request.form.get("notes") or None,
         group_id,
         group_expense_num,
         repair_id,
         maintenance_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

@app.route("/expenses/update/<int:expense_id>", methods=["POST"])
def update_expense(expense_id):
    db = get_db()
    current = db.execute(
        "SELECT group_id, group_expense_num, repair_id, maintenance_id FROM expenses WHERE id = ?",
        (expense_id,)
    ).fetchone()

    new_group_id      = resolve_group_id(db, request.form.get("group_id"), request.form.get("group_name"),
                                        request.form.get("group_type", "R"))
    new_repair_id     = request.form.get("repair_id") or None
    new_maintenance_id = request.form.get("maintenance_id") or None
    group_changed     = str(new_group_id or "") != str(current["group_id"] or "")

    # Recalculate group_expense_num if group changed
    group_expense_num = current["group_expense_num"]
    if group_changed:
        if new_group_id:
            row = db.execute(
                "SELECT COALESCE(MAX(group_expense_num), 0) AS m FROM expenses "
                "WHERE group_id = ? AND id != ?",
                (new_group_id, expense_id)
            ).fetchone()
            group_expense_num = row["m"] + 1
        else:
            group_expense_num = None

    # Cascade group change to the linked repair (old or new)
    if group_changed:
        target_repair = new_repair_id or current["repair_id"]
        if target_repair:
            db.execute("UPDATE repairs SET group_id = ? WHERE id = ?",
                       (new_group_id, target_repair))
        target_maint = new_maintenance_id or current["maintenance_id"]
        if target_maint:
            db.execute("UPDATE maintenance SET group_id = ? WHERE id = ?",
                       (new_group_id, target_maint))

    # If a NEW repair/maintenance link is being set (without a group change),
    # sync that record's group to match this expense
    if not group_changed:
        if new_repair_id and new_repair_id != str(current["repair_id"] or ""):
            db.execute("UPDATE repairs SET group_id = ? WHERE id = ?",
                       (new_group_id, new_repair_id))
        if new_maintenance_id and new_maintenance_id != str(current["maintenance_id"] or ""):
            db.execute("UPDATE maintenance SET group_id = ? WHERE id = ?",
                       (new_group_id, new_maintenance_id))

    db.execute(
        """UPDATE expenses SET title=?, category=?, cost=?, purchase_month=?, vendor=?,
           mechanic=?, notes=?, group_id=?, group_expense_num=?, repair_id=?, maintenance_id=?
           WHERE id=?""",
        (request.form["title"],
         request.form.get("category") or None,
         request.form.get("cost") or 0,
         request.form.get("purchase_month") or None,
         request.form.get("vendor") or None,
         request.form.get("mechanic") or None,
         request.form.get("notes") or None,
         new_group_id,
         group_expense_num,
         new_repair_id,
         new_maintenance_id,
         expense_id)
    )
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

@app.route("/expenses/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

@app.route("/groups/add", methods=["POST"])
def add_group():
    db = get_db()
    type_ = request.form.get("type", "R")
    count = db.execute(
        "SELECT COUNT(*) AS c FROM groups WHERE type = ?", (type_,)
    ).fetchone()["c"]
    code = f"{type_}{count + 1}"
    db.execute(
        "INSERT INTO groups (name, type, code, notes) VALUES (?, ?, ?, ?)",
        (request.form["name"], type_, code, request.form.get("notes") or None)
    )
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

@app.route("/groups/delete/<int:group_id>", methods=["POST"])
def delete_group(group_id):
    db = get_db()
    db.execute("UPDATE expenses SET group_id = NULL, group_expense_num = NULL WHERE group_id = ?", (group_id,))
    db.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    db.commit()
    db.close()
    return redirect(url_for("expenses"))

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
    groups = [dict(g) for g in db.execute("SELECT * FROM groups ORDER BY type, id").fetchall()]
    db.close()
    return render_template("wishlist.html", items=items, groups=groups,
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
    from datetime import date
    db = get_db()
    item = dict(db.execute("SELECT * FROM wishlist WHERE id = ?", (item_id,)).fetchone())

    promote_to = request.form.get("promote_to", "R")
    group_choice = request.form.get("group_id", "")

    group_id = None
    if group_choice == "new":
        group_name = request.form.get("group_name") or item["name"]
        count = db.execute(
            "SELECT COUNT(*) AS c FROM groups WHERE type = ?", (promote_to,)
        ).fetchone()["c"]
        code = f"{promote_to}{count + 1}"
        cursor = db.execute(
            "INSERT INTO groups (name, type, code) VALUES (?, ?, ?)",
            (group_name, promote_to, code)
        )
        group_id = cursor.lastrowid
    elif group_choice:
        group_id = int(group_choice)

    if promote_to == "R":
        record_cursor = db.execute(
            """INSERT INTO repairs (title, status, category, cost, purchase_link, notes, group_id)
               VALUES (?, 'Not Started', ?, ?, ?, ?, ?)""",
            (item["name"], item.get("category"),
             item.get("estimated_price") or 0,
             item.get("link"), item.get("notes"), group_id)
        )
        dest = "repairs"
    else:
        record_cursor = db.execute(
            """INSERT INTO maintenance (task, status, notes, group_id)
               VALUES (?, 'Pending', ?, ?)""",
            (item["name"], item.get("notes"), group_id)
        )
        dest = "maintenance"

    if item.get("estimated_price"):
        group_expense_num = None
        if group_id:
            row = db.execute(
                "SELECT COALESCE(MAX(group_expense_num), 0) AS m FROM expenses WHERE group_id = ?",
                (group_id,)
            ).fetchone()
            group_expense_num = row["m"] + 1
        exp_repair_id      = record_cursor.lastrowid if promote_to == "R" else None
        exp_maintenance_id = record_cursor.lastrowid if promote_to == "M" else None
        db.execute(
            """INSERT INTO expenses
               (title, category, cost, purchase_month, group_id, group_expense_num,
                repair_id, maintenance_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (item["name"], item.get("category"),
             item.get("estimated_price"),
             date.today().strftime("%Y-%m"),
             group_id, group_expense_num,
             exp_repair_id, exp_maintenance_id)
        )

    db.execute("DELETE FROM wishlist WHERE id = ?", (item_id,))
    db.commit()
    db.close()
    return redirect(url_for(dest))

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
    app.run(debug=True, port=5001)
