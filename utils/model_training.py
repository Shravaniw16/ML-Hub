import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")  # CRITICAL FIX for server

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_squared_error
)

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer


# ==============================
# STATIC DIRECTORY
# ==============================
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)


# ==============================
# Helper: normalize Yes/No labels
# ==============================
def normalize_target(y):
    if y.dtype == object:
        y = y.astype(str).str.strip().str.lower()

        if set(y.unique()).issubset({"yes", "no"}):
            return y.map({"yes": 1, "no": 0})
        
        if set(y.unique()).issubset({"positive", "negative"}):
            return y.map({"positive": 1, "negative": 0})

        if set(y.unique()).issubset({"true", "false"}):
            return y.map({"true": 1, "false": 0})

        if set(y.unique()).issubset({"pass", "fail"}):
            return y.map({"pass": 1, "fail": 0})

        if set(y.unique()).issubset({"1", "0"}):
            return y.astype(int)

    return y


# ==============================
# Main training function
# ==============================
def train_model(filepath, target, model_type, data_type="structured"):

    # Load dataset
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    if target not in df.columns:
        return {"error": "Target column not found"}

    y = df[target]
    y = normalize_target(y)

    # ==============================
    # DATA TYPE SWITCH (IMPORTANT)
    # ==============================
    if data_type == "structured":

        # Structured numeric / categorical data
        X = df.drop(columns=[target])
        X = pd.get_dummies(X)

    elif data_type == "unstructured":

        # Unstructured text data
        if "cleaned_text" not in df.columns:
            return {"error": "cleaned_text column missing"}

        vectorizer = TfidfVectorizer(max_features=3000)
        X = vectorizer.fit_transform(df["cleaned_text"])

    else:
        return {"error": "Invalid data type"}

    # ==============================
    # Train / Test split
    # ==============================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ==============================
    # CLASSIFICATION MODELS
    # ==============================
    if model_type in ["logistic", "random_forest"]:

        if model_type == "logistic":
            model = LogisticRegression(max_iter=1000)
            model_name = "Logistic Regression"

        else:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model_name = "Random Forest Classifier"

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # ----- Confusion Matrix -----
        cm = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix")
        plt.tight_layout()

        cm_path = os.path.join(STATIC_DIR, "confusion_matrix.png")
        plt.savefig(cm_path)
        plt.close()

        result = {
            "model": model_name,
            "data_type": data_type,
            "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
            "precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
            "recall": round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
            "f1": round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
            "confusion_matrix": "/static/confusion_matrix.png"
        }

        # ----- Feature Importance (Structured RF only) -----
        if model_type == "random_forest" and data_type == "structured":
            fi_df = pd.DataFrame({
                "feature": X.columns,
                "importance": model.feature_importances_
            }).sort_values(by="importance", ascending=False).head(10)

            plt.figure(figsize=(8, 5))
            sns.barplot(x="importance", y="feature", data=fi_df)
            plt.title("Top 10 Feature Importance")
            plt.tight_layout()

            fi_path = os.path.join(STATIC_DIR, "feature_importance.png")
            plt.savefig(fi_path)
            plt.close()

            result["feature_importance"] = "/static/feature_importance.png"

        return result

    # ==============================
    # REGRESSION MODELS
    # ==============================
    if model_type == "linear":
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {
            "model": "Linear Regression",
            "data_type": data_type,
            "mse": round(mean_squared_error(y_test, y_pred), 2)
        }

    if model_type == "random_forest_reg":
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        return {
            "model": "Random Forest Regressor",
            "data_type": data_type,
            "mse": round(mean_squared_error(y_test, y_pred), 2)
        }

    # ==============================
    # Unsupported
    # ==============================
    return {"error": "Unsupported model type"}
