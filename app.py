from flask import Flask, request, jsonify, session, send_from_directory, render_template
from flask_cors import CORS
import os
import hashlib
import sqlite3
from datetime import datetime
import pandas as pd
from utils.data_analysis import analyze_dataset
from utils.model_training import train_model
from database import save_trained_model, get_user_models

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from database import save_dataset
from utils.audio_analysis import analyze_audio
from utils.video_analysis import analyze_video

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mlhub.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ===============================
# FLASK CONFIG
# ===============================
app = Flask(__name__, static_folder="static")
app.secret_key = "mlhub-secret-key"

CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500"]
)


# ===============================
# GLOBAL MEMORY
# ===============================
LAST_TRAINING_RESULT = None
LAST_DATASET_SUMMARY = None

# ===============================
# DATABASE CONNECTION
# ===============================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ===============================
# AUTH ROUTES
# ===============================
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "All fields required"}), 400

        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db()
        cur = conn.cursor()

        # Check existing user
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            return jsonify({"error": "User already exists"}), 409

        # Insert user
        cur.execute("""
            INSERT INTO users (name, email, password, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return jsonify({"message": "Registration successful"})

    except Exception as e:
        print("🔥 SIGNUP ERROR:", e)   # <-- SEE THIS IN TERMINAL
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM users
        WHERE email = ? AND password = ?
    """, (email, hashed))

    user = cur.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ SESSION FIX
    session["email"] = email
    

    return jsonify({"message": "Login successful"})


@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# ===============================
# FILE UPLOAD + ANALYSIS
# ===============================
@app.route("/upload", methods=["POST"])
def upload_file():
    global LAST_DATASET_SUMMARY

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = file.filename.lower()
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    

    # ===============================
    # CSV FILE → DATASET + ML ANALYSIS
    # ===============================
    if filename.endswith(".csv"):
        analysis = analyze_dataset(filepath)

        LAST_DATASET_SUMMARY = {
            "File Name": file.filename,
            "Total Rows": analysis["total_rows"],
            "Total Columns": analysis["total_columns"],
            "Columns": ", ".join(analysis["preview"][0].keys())
        }

        analysis["filepath"] = filepath
        analysis["columns"] = list(analysis["preview"][0].keys())

        save_dataset({
            "user_id": session.get("email"),
            "filename": file.filename,
            "filepath": filepath,
            "rows": analysis["total_rows"],
            "columns": analysis["total_columns"]
        })

        return jsonify(analysis)

    # ===============================
    # AUDIO FILE → FEATURE EXTRACTION
    # ===============================
    elif filename.endswith((".wav", ".mp3")):
        from utils.audio_analysis import analyze_audio

        audio_result = analyze_audio(filepath)
        audio_result["filename"] = file.filename
        audio_result["type"] = "audio"

        return jsonify(audio_result)

    # ===============================
    # VIDEO FILE → METADATA ANALYSIS
    # ===============================
    elif filename.endswith((".mp4", ".avi", ".mov")):
        from utils.video_analysis import analyze_video

        video_result = analyze_video(filepath)
        video_result["filename"] = file.filename
        video_result["type"] = "video"

        return jsonify(video_result)

    # ===============================
    # UNSUPPORTED FILE TYPE
    # ===============================
    else:
        return jsonify({"error": "Unsupported file type"}), 400
@app.route("/clean-data", methods=["POST"])
def clean_data():
    data = request.get_json()
    filepath = data.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Dataset not found"}), 400

    df = pd.read_csv(filepath)

    # ---------------- CLEANING ----------------
    df = df.drop_duplicates()
    df = df.dropna()

    # Sentiment label normalization
    if "sentiment" in df.columns:
        df["label"] = df["sentiment"].map({
            "positive": 1,
            "negative": 0
        })

    clean_path = filepath.replace(".csv", "_clean.csv")
    df.to_csv(clean_path, index=False)

    # 🔥 THIS IS THE MOST IMPORTANT LINE
    session["cleaned_dataset_path"] = clean_path

    return jsonify({
        "message": "Dataset cleaned successfully",
        "cleaned_path": clean_path,
        "rows": len(df),
        "columns": list(df.columns)
    })
@app.route("/dataset-analytics", methods=["GET"])
def dataset_analytics():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    dataset_path = session.get("last_uploaded_dataset")

    if not dataset_path or not os.path.exists(dataset_path):
        return jsonify({"error": "Dataset not found"}), 400

    df = pd.read_csv(dataset_path)

    response = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns)
    }

    # If sentiment / category column exists
    for col in df.columns:
        if df[col].dtype == "object" or df[col].nunique() < 10:
            response["category_column"] = col
            response["category_counts"] = df[col].value_counts().to_dict()
            break

    return jsonify(response)


@app.route("/download-clean-data")
def download_clean_data():
    path = request.args.get("path")

    if not path or not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=True)

@app.route("/upload-unstructured", methods=["POST"])
def upload_unstructured():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename.lower()

    save_path = os.path.join(UPLOAD_FOLDER, "raw_text")
    os.makedirs(save_path, exist_ok=True)

    filepath = os.path.join(save_path, file.filename)
    file.save(filepath)

    if filename.endswith(".txt"):
        return jsonify({
            "message": "Text file uploaded successfully",
            "filepath": filepath,
            "type": "text"
        })

    elif filename.endswith(".csv"):
        return jsonify({
            "message": "CSV file uploaded successfully",
            "filepath": filepath,
            "type": "csv"
        })

    else:
        return jsonify({"error": "Unsupported unstructured file type"}), 400
from utils.text_cleaning import process_text_file

@app.route("/clean-unstructured", methods=["POST"])
def clean_unstructured():
    data = request.get_json()
    filepath = data.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 400

    df = process_text_file(filepath)

    preview = df.head(10).to_dict(orient="records")

    return jsonify({
        "message": "Text cleaned successfully",
        "total_records": len(df),
        "preview": preview,
        "columns": list(df.columns)
    })
@app.route("/dashboard-dataset-data")
def dashboard_dataset_data():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Use cleaned dataset if exists
    cleaned_path = session.get("cleaned_dataset_path")
    if not cleaned_path or not os.path.exists(cleaned_path):
        return jsonify({"error": "No cleaned dataset found"}), 400

    import pandas as pd
    df = pd.read_csv(cleaned_path)

    response = {
        "total_rows": len(df),
        "columns": list(df.columns),
    }

    # Example: sentiment / label distribution
    if "label" in df.columns:
        counts = df["label"].value_counts().to_dict()
        response["label_distribution"] = counts

    return jsonify(response)

from flask import send_file
import uuid

@app.route("/download-clean-csv", methods=["POST"])
def download_clean_csv():
    data = request.get_json()
    filepath = data.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 400

    # Clean again (safe)
    df = process_text_file(filepath)

    clean_filename = f"cleaned_{uuid.uuid4().hex[:6]}.csv"
    clean_path = os.path.join(UPLOAD_FOLDER, clean_filename)
    df.to_csv(clean_path, index=False)

    # store for training/dashboard
    session["cleaned_dataset_path"] = clean_path

    # ✅ SEND CSV FILE (THIS IS THE KEY)
    return send_file(
        clean_path,
        as_attachment=True,
        download_name="cleaned_unstructured_data.csv"
    )

from utils.powerbi_analysis import analyze_for_dashboard
from flask import send_file

@app.route("/powerbi-page")
def powerbi_page():
    return render_template("powerbi_dashboard.html")


@app.route("/powerbi-upload", methods=["POST"])
def powerbi_upload():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = analyze_for_dashboard(filepath)

    # store for download
    session["powerbi_dataset"] = filepath

    return jsonify(result)


@app.route("/powerbi-download")
def powerbi_download():
    path = session.get("powerbi_dataset")

    if not path or not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=True)


# ===============================
# MODEL TRAINING
# ===============================
@app.route("/train", methods=["POST"])
def train():
    global LAST_TRAINING_RESULT

    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        filepath = data.get("filepath")
        target = data.get("target")
        model_type = data.get("model")
        data_type = data.get("data_type", "structured")  # 👈 NEW

        if not filepath or not os.path.exists(filepath):
            return jsonify({"error": "Dataset file not found"}), 400

        if not target or not model_type:
            return jsonify({"error": "Target or model missing"}), 400

        # ===============================
        # CALL UNIFIED TRAINING FUNCTION
        # ===============================
        result = train_model(
            filepath=filepath,
            target=target,
            model_type=model_type,
            data_type=data_type
        )

        if "error" in result:
            return jsonify(result), 400

        # ===============================
        # SAVE TO DATABASE
        # ===============================
        save_trained_model({
            "user_email": session["email"],
            "dataset_name": os.path.basename(filepath),
            "target_column": target,
            "model_type": result.get("model"),
            "accuracy": result.get("accuracy"),
            "precision": result.get("precision"),
            "recall": result.get("recall"),
            "f1": result.get("f1")
        })

        LAST_TRAINING_RESULT = result
        return jsonify(result)

    except Exception as e:
        print("🔥 TRAIN ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ===============================
# USER MODELS DASHBOARD
# ===============================
@app.route("/my-models")
def my_models():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    models = get_user_models(session["email"])
    return jsonify(models)
@app.route("/analysis-page")
def analysis_page():
    return render_template("analysis.html")

# ===============================
# PDF REPORT
# ===============================
@app.route("/download-report")
def download_report():
    if not LAST_TRAINING_RESULT or not LAST_DATASET_SUMMARY:
        return "No training result found", 400

    pdf_path = os.path.join(STATIC_FOLDER, "model_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # PAGE 1 – DATASET SUMMARY
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Dataset Summary")

    c.setFont("Helvetica", 12)
    y = height - 100
    for k, v in LAST_DATASET_SUMMARY.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 25

    c.showPage()

    # PAGE 2 – MODEL PERFORMANCE
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Model Performance Report")

    c.setFont("Helvetica", 12)
    y = height - 100
    for k, v in LAST_TRAINING_RESULT.items():
        if k not in ["confusion_matrix", "feature_importance"]:
            c.drawString(50, y, f"{k.upper()} : {v}")
            y -= 25
            

    # Confusion Matrix Image
    cm = LAST_TRAINING_RESULT.get("confusion_matrix")
    if cm:
        cm_path = cm.lstrip("/")
        if os.path.exists(cm_path):
            img = ImageReader(cm_path)
            c.drawImage(img, 50, y - 300, width=300, height=300)

    c.showPage()
    c.save()
    

    return send_from_directory(STATIC_FOLDER, "model_report.pdf", as_attachment=True)

# ===============================
# FRONTEND ROUTES
# ===============================

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/train-page")
def train_page():
    return render_template("train.html")

@app.route("/my-models-page")
def my_models_page():
    return render_template("my_models.html")

@app.route("/report-page")
def report_page():
    return render_template("report.html")


def is_admin():
    return session.get("email") == "admin@mlhub.com"
@app.route("/admin-page")
def admin_page():
    if not is_admin():
        return "Unauthorized", 403
    return render_template("admin.html")
@app.route("/admin/users")
def admin_users():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users")
    users = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(users)
@app.route("/admin/datasets")
def admin_datasets():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT filename, filepath, rows, columns, uploaded_at
        FROM datasets
    """)
    data = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(data)
@app.route("/admin/models")
def admin_models():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_email, dataset_name, target_column,
               model_type, accuracy, precision, recall, f1, created_at
        FROM trained_models
    """)
    models = [dict(row) for row in cur.fetchall()]
    conn.close()

    return jsonify(models)
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    cur = conn.cursor()

    # Total datasets
    cur.execute(
        "SELECT COUNT(*) FROM datasets WHERE user_id = ?",
        (session["email"],)
    )
    total_datasets = cur.fetchone()[0]

    # Total models
    cur.execute(
        "SELECT COUNT(*) FROM trained_models WHERE user_email = ?",
        (session["email"],)
    )
    total_models = cur.fetchone()[0]

    # Best accuracy
    cur.execute("""
        SELECT MAX(accuracy) FROM trained_models
        WHERE user_email = ?
    """, (session["email"],))
    best_accuracy = cur.fetchone()[0]

    # Last trained model
    cur.execute("""
        SELECT dataset_name, model_type, created_at
        FROM trained_models
        WHERE user_email = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["email"],))
    last_model = cur.fetchone()

    conn.close()

    return jsonify({
        "total_datasets": total_datasets,
        "total_models": total_models,
        "best_accuracy": best_accuracy,
        "last_model": dict(last_model) if last_model else None
    })
@app.route("/dashboard-data")
def dashboard_data():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if not LAST_TRAINING_RESULT:
        return jsonify({"error": "No training data found"}), 400

    return jsonify({
        "model": LAST_TRAINING_RESULT.get("model"),
        "accuracy": LAST_TRAINING_RESULT.get("accuracy"),
        "precision": LAST_TRAINING_RESULT.get("precision"),
        "recall": LAST_TRAINING_RESULT.get("recall"),
        "f1": LAST_TRAINING_RESULT.get("f1"),
        "confusion_matrix": LAST_TRAINING_RESULT.get("confusion_matrix"),
        "feature_importance": LAST_TRAINING_RESULT.get("feature_importance")
    })

@app.route("/dashboard-analytics-page")
def dashboard_analytics_page():
    return render_template("dashboard_analytics.html")

@app.route("/dashboard-page")
def dashboard_page():
    return render_template("dashboard.html")
@app.route("/")
def intro():
    return render_template("intro.html")
@app.route("/index-page")
def index_page():
    return render_template("index.html")

# ===============================
# RUN
# ===============================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )
