import openai
import pandas as pd
import streamlit as st
import json

openai.api_key = st.secrets.get("OPENAI_API_KEY")

def extract_tables_from_pdf(uploaded_file) -> pd.DataFrame:
    """
    Sends a full PDF file to GPT-4 Vision via the file API,
    asks it to return a clean, structured P&L table in JSON format.
    """
    st.info("Uploading PDF to OpenAI for table extraction...")

    try:
        # Upload file to OpenAI
        file_response = openai.files.create(
            file=uploaded_file,
            purpose="assistants"
        )
        file_id = file_response.id

        # Send file to GPT-4o with instructions
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a financial data analyst. "
                    "Extract the P&L table from the uploaded PDF and return it as a JSON array of objects. "
                    "Each object should represent one row. Remove currency symbols, commas, and non-numeric characters."
                )},
                {"role": "user", "content": [
                    {"type": "text", "text": "Please extract the table from this PDF and return it as clean JSON."},
                    {"type": "file", "file_id": file_id}
                ]}
            ],
            max_tokens=2000
        )

        text = response.choices[0].message.content
        data = json.loads(text)
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"OpenAI file extraction failed: {e}")
        raise ValueError("Failed to extract table from PDF using GPT.")
