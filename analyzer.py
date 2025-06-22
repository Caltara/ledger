import pandas as pd

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").dropna(axis=1, how="all").copy()
    df.columns = df.columns.str.strip()

    numeric_cols = []
    for col in df.columns:
        if col.lower() == "line item":
            continue
        try:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[$,]", "", regex=True)
                .str.replace("%", "", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
            numeric_cols.append(col)
        except Exception:
            pass

    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df

def detect_irregularities(df: pd.DataFrame, threshold=5):
    pct_change_cols = [col for col in df.columns if "CHANGE" in col.upper()]
    if not pct_change_cols:
        raise ValueError("No % CHANGE columns found in data for analysis.")

    anomalies = []
    for idx, row in df.iterrows():
        for col in pct_change_cols:
            try:
                val_str = str(row[col]).replace("%", "").strip()
                val = float(val_str)
                if abs(val) >= threshold:
                    anomalies.append(
                        {
                            "Line Item": row.get("Line Item", f"Row {idx}"),
                            "Change Type": col,
                            "Change (%)": f"{val:+.2f}%",
                            "Value": row.get(col.replace("CHANGE", "").strip(), ""),
                        }
                    )
            except Exception:
                continue

    return anomalies

def generate_summary(df: pd.DataFrame) -> dict:
    summary = {}
    numeric_cols = [
        col for col in df.columns if col.lower() != "line item" and pd.api.types.is_numeric_dtype(df[col])
    ]
    for col in numeric_cols:
        col_sum = df[col].sum()
        summary[col] = f"${col_sum:,.2f}"
    summary["Total Line Items"] = len(df)
    return summary
