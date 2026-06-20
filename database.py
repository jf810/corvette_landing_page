import sqlite3

DATABASE = "corvette.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            category TEXT,
            cost REAL DEFAULT 0,
            start_date TEXT,
            start_date_unknown INTEGER DEFAULT 0,
            finish_date TEXT,
            finish_date_unknown INTEGER DEFAULT 0,
            time_taken TEXT,
            paid_for_service INTEGER DEFAULT 0,
            mechanic TEXT,
            vendor TEXT,
            purchase_link TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            start_date TEXT,
            start_date_unknown INTEGER DEFAULT 0,
            finish_date TEXT,
            finish_date_unknown INTEGER DEFAULT 0,
            time_taken TEXT,
            paid_for_service INTEGER DEFAULT 0,
            mechanic TEXT,
            vendor TEXT,
            purchase_link TEXT,
            recurring INTEGER DEFAULT 0,
            frequency_miles INTEGER,
            frequency_months_min INTEGER,
            frequency_months_max INTEGER,
            next_due_date TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'Repair/Upgrade',
            category TEXT,
            estimated_price REAL,
            link TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            folder TEXT DEFAULT 'General',
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")

def migrate_db():
    """Safely adds new columns to existing tables without losing data."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    new_columns = [
        "ALTER TABLE repairs ADD COLUMN paid_for_service INTEGER DEFAULT 0",
        "ALTER TABLE repairs ADD COLUMN mechanic TEXT",
        "ALTER TABLE repairs ADD COLUMN category TEXT",
        "ALTER TABLE maintenance ADD COLUMN paid_for_service INTEGER DEFAULT 0",
        "ALTER TABLE maintenance ADD COLUMN mechanic TEXT",
    ]
    for sql in new_columns:
        try:
            c.execute(sql)
        except Exception:
            pass  # column already exists — skip
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    init_db()
    migrate_db()
