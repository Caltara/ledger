import pandas as pd
import fitz  # PyMuPDF
import openai
import streamlit as st

def extract_tables_from_pdf(uploaded_file):
    all_text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text = page.get_text()
                all_text += text + "\n"

        if not all_text.strip():
            raise ValueError("No extractable text found in PDF.")
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You're a financial data analyst. Extract tables from a P&L report and return them as JSON."
                },
                {
                    "role": "user",
                    "content": all_text
                }
            ],
            response_format="json"
        )

        extracted_data = response.choices[0].message.content
        df = pd.read_json(StringIO(extracted_data))
        return df

    except Exception as e:
        raise ValueError("❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: " + str(e))
