import sqlite3
import os

DB_NAME = "mlhub.db"


# ===============================
# GET DATABASE CONNECTION
# ===============================
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ===============================
# SAVE TRAINED MODEL
# ===============================
def save_trained_model(data):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trained_models (
            user_email,
            dataset_name,
            target_column,
            model_type,
            accuracy,
            precision,
            recall,
            f1
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["user_email"],
        data["dataset_name"],
        data["target_column"],
        data["model_type"],
        data["accuracy"],
        data["precision"],
        data["recall"],
        data["f1"]
    ))

    conn.commit()
    conn.close()

def save_dataset(data):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO datasets (
            user_id,
            filename,
            filepath,
            rows,
            columns,
            uploaded_at
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (
        data["user_id"],
        data["filename"],
        data["filepath"],
        data["rows"],
        data["columns"]
    ))

    conn.commit()
    conn.close()

# ===============================
# GET USER MODELS (DASHBOARD)
# ===============================
def get_user_models(email):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            dataset_name,
            target_column,
            model_type,
            accuracy,
            precision,
            recall,
            f1,
            created_at
        FROM trained_models
        WHERE user_email=?
        ORDER BY created_at DESC
    """, (email,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]
