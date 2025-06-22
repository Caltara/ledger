import pandas as pd
from sklearn.preprocessing import StandardScaler

def clean_and_convert(df):
    df.columns = [col.strip().lower() for col in df.columns]
    df = df.dropna(how='all')
    for col in df.columns[1:]:
        df[col] = df[col].replace('[\$,]', '', regex=True).astype(float)
    return df

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
