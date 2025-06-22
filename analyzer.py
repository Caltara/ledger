import pandas as pd

def clean_and_convert(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r'[\$,,%]', '', regex=True)
            df[col] = df[col].str.replace(',', '', regex=False)
            try:
                df[col] = df[col].astype(float)
            except:
                pass
    return df

def format_for_report(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == float or df[col].dtype == int:
            if "change" in col.lower():
                df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
            else:
                df[col] = df[col].map(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
    return df

def detect_irregularities(df, threshold=5.0):
    anomalies = []
    for _, row in df.iterrows():
        for col in df.columns:
            if "change" in col.lower():
                try:
                    if abs(float(row[col])) >= threshold:
                        anomalies.append(row.to_dict())
                        break
                except:
                    continue
    return anomalies

def generate_summary(df):
    df_clean = clean_and_convert(df.copy())
    change_columns = [col for col in df_clean.columns if "change" in col.lower()]
    total_changes = {}

    for col in change_columns:
        try:
            valid_vals = df_clean[col].dropna()
            avg_change = valid_vals.mean()
            total_changes[col] = f"{avg_change:.2f}%"
        except:
            continue

    if not total_changes:
        return "No valid change data available to summarize."

    summary = "\n".join([f"- **{col}**: Average change of **{val}**" for col, val in total_changes.items()])
    return summary
