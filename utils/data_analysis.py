import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ===============================
# Ensure charts directory exists
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART_DIR = os.path.join(BASE_DIR, "static", "charts")
os.makedirs(CHART_DIR, exist_ok=True)


def analyze_dataset(filepath):
    df = pd.read_csv(filepath)

    # ===============================
    # BASIC METRICS
    # ===============================
    total_rows = int(df.shape[0])
    total_columns = int(df.shape[1])

    missing_percent = round(
        (df.isnull().sum().sum() / max(df.size, 1)) * 100, 2
    )
    duplicate_rows = int(df.duplicated().sum())

    health_score = max(
        0,
        int(100 - missing_percent - (duplicate_rows / max(total_rows, 1)) * 10)
    )

    preview = df.head(5).fillna("").to_dict(orient="records")
    data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

    charts = []

    # ===============================
    # 1. TARGET DISTRIBUTION
    # ===============================
    target_col = df.columns[0]

    plt.figure(figsize=(6, 4))
    df[target_col].value_counts().head(10).plot(
        kind="bar",
        color="#4f46e5"
    )
    plt.title("Target Distribution")
    plt.xlabel(target_col)
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    target_path = os.path.join(CHART_DIR, "target_distribution.png")
    plt.savefig(target_path, dpi=150)
    plt.close()
    charts.append("/static/charts/target_distribution.png")

    # ===============================
    # 2. NUMERICAL HISTOGRAMS
    # ===============================
    num_cols = df.select_dtypes(include="number").columns.tolist()

    for col in num_cols[:2]:
        plt.figure(figsize=(6, 4))
        plt.hist(df[col], bins=25, color="#22c55e", edgecolor="black")
        plt.title(f"{col} Distribution")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.tight_layout()

        hist_name = f"{col}_hist.png"
        hist_path = os.path.join(CHART_DIR, hist_name)
        plt.savefig(hist_path, dpi=150)
        plt.close()
        charts.append(f"/static/charts/{hist_name}")

    # ===============================
    # 3. CORRELATION HEATMAP
    # ===============================
    if len(num_cols) >= 2:
        plt.figure(figsize=(6, 5))
        sns.heatmap(
            df[num_cols].corr(),
            annot=True,
            cmap="coolwarm",
            square=True,
            fmt=".2f"
        )
        plt.title("Correlation Heatmap")
        plt.tight_layout()

        heatmap_path = os.path.join(CHART_DIR, "correlation_heatmap.png")
        plt.savefig(heatmap_path, dpi=150)
        plt.close()
        charts.append("/static/charts/correlation_heatmap.png")

    # ===============================
    # FINAL RESPONSE
    # ===============================
    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "missing_percent": missing_percent,
        "duplicate_rows": duplicate_rows,
        "health_score": health_score,
        "preview": preview,
        "data_types": data_types,
        "charts": charts
    }
