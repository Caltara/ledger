import pandas as pd

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"[$,%]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="ignore")

    return df

def detect_irregularities(df: pd.DataFrame) -> list:
    change_cols = [col for col in df.columns if "%" in col]
    output = []

    for _, row in df.iterrows():
        for col in change_cols:
            try:
                val = float(str(row[col]).replace("%", "").replace(",", "").strip())
                if abs(val) >= 5:
                    output.append({
                        "Line Item": row.get("Line Item", "Unknown"),
                        col: f"{val:.2f}%"
                    })
            except:
                continue
    return output
