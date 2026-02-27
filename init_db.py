import sqlite3

conn = sqlite3.connect("mlhub.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS trained_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    dataset_name TEXT,
    target_column TEXT,
    model_type TEXT,
    accuracy REAL,
    precision REAL,
    recall REAL,
    f1 REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ trained_models table created")
