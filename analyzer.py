import pandas as pd

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame:
    - Converts currency/percent strings to numeric for calculation
    - Keeps original values in a formatted copy
    """
    cleaned = df.copy()

    for col in cleaned.columns:
        if col.lower() == "line item":
            continue

        # Internal cleaning: remove $ and % to convert to float
        cleaned[col] = cleaned[col].replace('[\$,%,]', '', regex=True)
        cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')

    cleaned = cleaned.fillna(0)
    return cleaned


def format_for_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats numeric columns to display with $, commas, and % as needed.
    Keeps the 'Line Item' column untouched.
    """
    formatted = df.copy()

    for col in formatted.columns:
        if col.lower() == "line item":
            continue

        if "change" in col.lower():
            # Format as percentage
            formatted[col] = formatted[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
        else:
            # Format as currency with comma
            formatted[col] = formatted[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")

    return formatted


def detect_irregularities(df: pd.DataFrame, threshold: float = 20.0) -> list:
    """
    Detects line items with % changes greater than the threshold.
    Returns a list of dictionaries with the anomalies.
    """
    anomalies = []
    if df.empty or df.shape[1] < 3:
        return anomalies

    for idx, row in df.iterrows():
        line_item = row.get("Line Item", "")
        for col in df.columns:
            if "change" in col.lower():
                try:
                    value = float(str(row[col]).replace('%', '').replace(',', '').strip())
                    if abs(value) > threshold:
                        anomalies.append({
                            "Line Item": line_item,
                            "Metric": col,
                            "Change": f"{value:.2f}%"
                        })
                except:
                    continue

    return anomalies


def generate_summary(df: pd.DataFrame) -> str:
    """
    Generates a summary comparing the first two time-based columns.
    Keeps $, commas, and % signs in the output.
    """
    if df.empty or df.shape[1] < 3:
        return "No data available to summarize."

    try:
        # Get first 2 columns after Line Item
        cols = [col for col in df.columns if col.lower() != "line item"]
        current_col, prev_col = cols[0], cols[1]

        current_total = df[current_col].replace('[\$,%,]', '', regex=True).astype(float).sum()
        prev_total = df[prev_col].replace('[\$,%,]', '', regex=True).astype(float).sum()

        change_pct = ((current_total - prev_total) / prev_total) * 100 if prev_total != 0 else 0
        direction = "increase" if change_pct >= 0 else "decrease"

        return (
            f"Total revenue for **{current_col}** is **${current_total:,.2f}**, "
            f"which is a **{abs(change_pct):.2f}% {direction}** from **{prev_col}**."
        )
    except Exception as e:
        return f"❌ Could not compute summary: {str(e)}"
