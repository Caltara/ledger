import pandas as pd

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the P&L dataframe by:
    - Removing currency and percent symbols
    - Converting numeric columns to float
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[\$,,%]", "", regex=True)
                .str.replace(",", "")
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def detect_irregularities(df: pd.DataFrame) -> list:
    """
    Detects line items with a percentage change greater than ±5%.
    Dynamically finds the best 'Line Item' column to describe each row.
    """
    output = []

    # Try to find a descriptive column name
    keywords = ["Line Item", "Account", "Item", "Description", "Name", "Service", "Product"]
    line_item_col = next(
        (col for col in df.columns if any(k.lower() in col.lower() for k in keywords)),
        None
    )

    # If no match, find a likely candidate: first non-numeric column with diverse values
    if not line_item_col:
        non_numeric = df.select_dtypes(include="object")
        for col in non_numeric.columns:
            if df[col].nunique() > 1:
                line_item_col = col
                break

    # Fallback to generic row naming
    if not line_item_col:
        df.insert(0, "Line Item", [f"Row {i+1}" for i in range(len(df))])
        line_item_col = "Line Item"

    # Identify percent change columns
    percent_cols = [col for col in df.columns if "%" in col or "CHANGE" in col.upper()]

    for _, row in df.iterrows():
        for col in percent_cols:
            try:
                val = row[col]
                if pd.isna(val):
                    continue
                if abs(float(val)) >= 5:
                    output.append({
                        "Line Item": row[line_item_col],
                        "Change Type": col,
                        "Change Amount": f"{float(val):.2f}%"
                    })
            except Exception:
                continue

    return output
