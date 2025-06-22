import pdfplumber
import pandas as pd

def extract_tables_from_pdf(file) -> pd.DataFrame:
    with pdfplumber.open(file) as pdf:
        all_data = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df)
    return pd.concat(all_data, ignore_index=True)
