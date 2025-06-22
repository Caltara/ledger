import openai
import streamlit as st
import pandas as pd
import io
from pdf2image import convert_from_bytes
from PIL import Image
import json

openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_tables_from_pdf(file) -> pd.DataFrame:
    images = convert_from_bytes(file.read())
    tables = []

    for i, image in enumerate(images):
        st.info(f"Processing page {i+1} with GPT-4o...")

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": (
                        "You are a financial analyst. Extract the Profit & Loss table from the image as JSON. "
                        "Output it as an array of objects like this:\n"
                        "[{\"Line Item\": \"Revenue\", \"Jan\": 10000, \"Feb\": 12000, ...}, ...]\n"
                        "Only return the JSON. No text or explanation."
                    )},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Extract the table from this page."},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_bytes.hex(), "detail": "high"}}
                    ]}
                ],
                max_tokens=1500
            )

            raw_text = response.choices[0].message.content
            data = json.loads(raw_text)
            df = pd.DataFrame(data)
            tables.append(df)

        except Exception as e:
            st.error(f"Page {i+1} failed: {e}")

    if not tables:
        raise ValueError("❌ GPT-4o could not extract any table from the PDF.")

    return pd.concat(tables, ignore_index=True)
