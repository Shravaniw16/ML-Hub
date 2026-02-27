import pandas as pd

def analyze_for_dashboard(filepath):
    df = pd.read_csv(filepath)

    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns)
    }

    categorical = {}
    numeric = {}

    for col in df.columns:
        if df[col].dtype == "object":
            categorical[col] = df[col].value_counts().to_dict()
        else:
            numeric[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean())
            }

    return {
        "summary": summary,
        "categorical": categorical,
        "numeric": numeric
    }
