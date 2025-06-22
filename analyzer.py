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
            df[col] = df[col].astype(str).str.replace(r"[$,%]", "", regex=True)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def detect_irregularities(df: pd.DataFrame) -> list:
    """
    Detects line items with a percentage change greater than ±5%.
    Dynamically finds the column used for line item names.
    """
    output = []

    # Dynamically find the line item column
    possible_labels = ["Line Item", "Item", "Account", "Name", "Description"]
    line_item_col = next((col for col in df.columns if col.strip() in possible_labels), None)

    if not line_item_col:
        # Fallback if no label found
        df.insert(0, "Line Item", [f"Row {i+1}" for i in range(len(df))])
        line_item_col = "Line Item"

    # Identify all columns that represent percentage change
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
                        "Change Amount": f"{val:.2f}%"
                    })
            except Exception:
                continue

    return output
