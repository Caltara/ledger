import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import tempfile
import re

def extract_tables_from_pdf(file) -> pd.DataFrame:
    all_data = []

    try:
        # Attempt to extract using pdfplumber (for text-based PDFs)
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_data.append(df)
        if all_data:
            return pd.concat(all_data, ignore_index=True)
    except Exception as e:
        print("pdfplumber failed:", e)

    # Fallback: use OCR on scanned or image-based PDFs
    try:
        images = convert_from_bytes(file.read())
        lines = []
        for image in images:
            text = pytesseract.image_to_string(image)
            lines += text.splitlines()

        # Try to detect table-like structure from OCR
        data = [re.split(r'\s{2,}|\t', line.strip()) for line in lines if line.strip()]
        data = [row for row in data if len(row) > 1]  # skip empty or one-word rows

        if len(data) < 2:
            raise ValueError("OCR did not extract a usable table.")

        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    except Exception as e:
        raise ValueError("Failed to extract data from PDF using OCR. Make sure the file includes a readable table.")
