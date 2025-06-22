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
            # Remove $ , % and convert to numeric
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"[\$,%]", "", regex=True)
                .str.replace(",", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def detect_irregularities(df: pd.DataFrame) -> list:
    """
    Detects line items with a percentage change greater than ±5%.
    Dynamically detects the best descriptive column for line items.
    """
    output = []

    # Priority keywords to find descriptive column
    possible_names = ["Line Item", "Account", "Item", "Description", "Name", "Service", "Product"]
    line_item_col = None

    # First try to find a column with any of the keywords in its name
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in possible_names):
            line_item_col = col
            break

    # If not found, fallback to first non-numeric column with many unique values and non-null values
    if not line_item_col:
        for col in df.columns:
            if df[col].dtype == object and df[col].nunique() > 5 and df[col].notna().sum() > 5:
                line_item_col = col
                break

    # Final fallback: create a generic "Line Item" column with row numbers
    if not line_item_col:
        df.insert(0, "Line Item", [f"Row {i+1}" for i in range(len(df))])
        line_item_col = "Line Item"

    # Find all columns that likely represent percent change
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
                        "Change Amount": f"{float(val):,.2f}%"  # format with commas and 2 decimals
                    })
            except Exception:
                continue

    return output
