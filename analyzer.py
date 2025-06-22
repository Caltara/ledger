import pandas as pd
from sklearn.ensemble import IsolationForest

def clean_and_convert(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(how='all', inplace=True)
    return df

def detect_irregularities(df: pd.DataFrame):
    if df.shape[1] <= 2:
        return []

    numeric_df = df.iloc[:, 1:]
    model = IsolationForest(contamination=0.15, random_state=42)
    outliers = model.fit_predict(numeric_df)

    anomalies = []
    for idx, val in enumerate(outliers):
        if val == -1:
            anomalies.append({
                "Line Item": df.iloc[idx, 0],
                "Values": numeric_df.iloc[idx].to_dict()
            })
    return anomalies
