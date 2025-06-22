import pandas as pd
import numpy as np

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()

    # Columns except 'Line Item' assumed numeric but may contain $, commas, or %
    cols = [col for col in df_clean.columns if col != "Line Item"]

    for col in cols:
        # Remove $ and commas
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .str.strip()
        )

        # Convert percentages like "14.22%" to 0.1422
        df_clean[col] = df_clean[col].apply(
            lambda x: float(x.strip('%')) / 100 if isinstance(x, str) and x.endswith('%') else x
        )

        # Convert to numeric; invalid parsing -> NaN
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    return df_clean

def detect_irregularities(df: pd.DataFrame, threshold_pct=0.3):
    """
    Detect irregularities where a month-over-month change is greater than threshold_pct (e.g. 30%)
    Returns a list of dicts with 'Line Item', 'Period', 'Change', and 'Note'.
    """

    anomalies = []
    cols = [col for col in df.columns if col != "Line Item"]

    # We compare each column to the previous one for % change
    for i in range(1, len(cols)):
        current_col = cols[i]
        prev_col = cols[i - 1]

        for idx, row in df.iterrows():
            prev_val = row[prev_col]
            curr_val = row[current_col]

            # Avoid division by zero or NaNs
            if pd.isna(prev_val) or pd.isna(curr_val) or prev_val == 0:
                continue

            change = (curr_val - prev_val) / abs(prev_val)

            if abs(change) >= threshold_pct:
                anomalies.append({
                    "Line Item": row["Line Item"],
                    "From": prev_col,
                    "To": current_col,
                    "Change": f"{change:.1%}",
                    "Prev Value": prev_val,
                    "Current Value": curr_val,
                    "Note": "Significant increase" if change > 0 else "Significant decrease"
                })

    return anomalies
