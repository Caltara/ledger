import pandas as pd

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"[$,%]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def detect_irregularities(df: pd.DataFrame) -> list:
    output = []
    if "Line Item" not in df.columns:
        df.insert(0, "Line Item", [f"Row {i+1}" for i in range(len(df))])

    percent_cols = [col for col in df.columns if "%" in col or "CHANGE" in col.upper()]
    
    for _, row in df.iterrows():
        for col in percent_cols:
            try:
                val = row[col]
                if pd.isna(val):
                    continue
                if abs(float(val)) >= 5:
                    output.append({
                        "Line Item": row["Line Item"],
                        "Change Type": col,
                        "Change Amount": f"{val:.2f}%"
                    })
            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")
                continue

    return output
