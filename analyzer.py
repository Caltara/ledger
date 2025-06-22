import pandas as pd

def clean_and_convert(df):
    df = df.copy()
    df.columns = [col.strip() for col in df.columns]

    currency_cols = [col for col in df.columns if any(char in col for char in ['$', 'Revenue', 'Income'])]
    percent_cols = [col for col in df.columns if '%' in col]

    for col in currency_cols:
        df[col] = df[col].replace('[\$,]', '', regex=True).replace(',', '', regex=True).astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in percent_cols:
        df[col] = df[col].replace('%', '', regex=True).astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def detect_irregularities(df):
    filtered = df.copy()
    percent_cols = [col for col in df.columns if '%' in col]

    if not percent_cols:
        return pd.DataFrame()

    filtered_rows = []
    for _, row in df.iterrows():
        for col in percent_cols:
            try:
                change = abs(float(row[col]))
                if change >= 5:
                    filtered_rows.append(row)
                    break
            except:
                continue

    return pd.DataFrame(filtered_rows)
