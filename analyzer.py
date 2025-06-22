import pandas as pd

def clean_and_convert(df):
    # Standardize column names
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # Drop fully empty rows
    df = df.dropna(how='all')

    # Ensure the first column is "line items"
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()

    # Try converting each remaining column to numeric, skip if it fails
    numeric_columns = []
    for col in df.columns[1:]:
        try:
            df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
            numeric_columns.append(col)
        except Exception:
            df.drop(columns=[col], inplace=True)

    if not numeric_columns:
        raise ValueError("No numeric columns were found to analyze. Please upload a CSV with actual financial figures.")

    return df[[df.columns[0]] + numeric_columns]
