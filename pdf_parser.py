import pdfplumber
import pandas as pd

def extract_tables_from_pdf(file) -> pd.DataFrame:
    all_data = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_data.append(df)

    if not all_data:
        raise ValueError("No tables were found in the PDF. Please upload a clear, structured P&L statement.")

    return pd.concat(all_data, ignore_index=True)
