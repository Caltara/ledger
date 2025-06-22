import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import re

# Try to extract tables from digital PDFs
def extract_tables_from_pdf(file) -> pd.DataFrame:
    all_data = []

    try:
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

    # Fallback to OCR
    try:
        file.seek(0)  # reset file pointer
        images = convert_from_bytes(file.read())
        text_blocks = []
        for image in images:
            text = pytesseract.image_to_string(image)
            text_blocks.append(text)

        full_text = "\n".join(text_blocks)
        return parse_ocr_text_to_dataframe(full_text)

    except Exception as e:
        raise ValueError("Failed to extract data from PDF using OCR. Make sure the file includes a readable table.")

# Parse OCR text to a basic DataFrame structure
def parse_ocr_text_to_dataframe(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    structured_rows = []

    for line in lines:
        if re.match(r'^\s*$', line):
            continue  # skip blank lines
        columns = re.split(r'\s{2,}|\t+', line.strip())
        if len(columns) >= 2:
            structured_rows.append(columns)

    if len(structured_rows) < 2:
        raise ValueError("OCR extracted text but no structured data was found.")

    max_cols = max(len(row) for row in structured_rows)
    structured_rows = [row + [''] * (max_cols - len(row)) for row in structured_rows]

    df = pd.DataFrame(structured_rows[1:], columns=structured_rows[0])
    return df

# Optional: Raw OCR text output
def extract_ocr_text(file) -> str:
    file.seek(0)
    images = convert_from_bytes(file.read())
    ocr_text = ""

    for image in images:
        text = pytesseract.image_to_string(image)
        ocr_text += text + "\n"

    return ocr_text
