import pandas as pd
from sklearn.preprocessing import StandardScaler

def clean_and_convert(df):
    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how='all')
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()

    numeric_columns = []
    for col in df.columns[1:]:
        try:
            # Remove $ signs, commas, spaces, and convert to float
            cleaned = df[col].astype(str).str.replace(r'[^\d.\-]', '', regex=True)
            df[col] = cleaned.astype(float)
            numeric_columns.append(col)
        except Exception:
            df.drop(columns=[col], inplace=True)

    if not numeric_columns:
        raise ValueError("No numeric columns found. Ensure your CSV contains numbers without text, formulas, or date ranges.")

    return df[[df.columns[0]] + numeric_columns]

def detect_irregularities(df, threshold=2.0):
    irregularities = []
    scaler = StandardScaler()
    values = scaler.fit_transform(df.iloc[:, 1:].T).T  # z-score by row

    for i, row in enumerate(values):
        for j, val in enumerate(row):
            if abs(val) > threshold:
                irregularities.append({
                    "line_item": df.iloc[i, 0],
                    "period": df.columns[j+1],
                    "z_score": round(val, 2),
                    "amount": df.iloc[i, j+1]
                })
    return irregularities
