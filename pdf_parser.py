import openai
import streamlit as st
import pandas as pd
import json

openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_tables_from_pdf(file) -> pd.DataFrame:
    try:
        st.info("Uploading PDF to OpenAI...")

        # Upload file to OpenAI
        file_response = openai.files.create(file=file, purpose="assistants")
        file_id = file_response.id

        # Send to GPT-4o with file tool
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You're a financial analyst. Extract the Profit & Loss table from this PDF and return it as JSON. "
                    "Each row should be a dictionary with clean keys and numeric values. Remove currency symbols, commas, and totals."
                )},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract and format the P&L table from this PDF."},
                    {"type": "file", "file_id": file_id}
                ]}
            ],
            max_tokens=2000
        )

        raw_text = response.choices[0].message.content
        data = json.loads(raw_text)
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"GPT file extraction failed: {e}")
        raise ValueError("Could not extract table from PDF using GPT.")
