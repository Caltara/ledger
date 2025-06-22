import pandas as pd

def format_for_report(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()

    for col in formatted.columns:
        if col != "Line Item":
            # Try to convert to float if not already
            try:
                formatted[col] = pd.to_numeric(formatted[col].replace('[\$,,%]', '', regex=True), errors='coerce')
            except Exception:
                pass

            # Format currency and percentages
            if "CHANGE" in col.upper():
                formatted[col] = formatted[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
            else:
                formatted[col] = formatted[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "")

    return formatted
