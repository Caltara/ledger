import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import openai
import base64
import io
import json
from PIL import Image

openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_tables_from_pdf(file) -> pd.DataFrame:
    try:
        st.info("Rendering first page of the PDF...")

        # Read PDF using PyMuPDF
        pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
        first_page = pdf_doc.load_page(0)
        pix = first_page.get_pixmap(dpi=200)

        # Convert to PNG and encode as base64
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_url = f"data:image/png;base64,{img_base64}"

        st.info("Sending image to GPT-4o...")

        # Call GPT-4o Vision with the image
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a financial analyst. Extract the Profit & Loss table from this image. "
                        "Return it as JSON. Each row should be a dictionary with fields like 'Line Item', 'Jan', 'Feb', etc."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract and format the P&L table from this image."},
                        {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                    ]
                }
            ],
            max_tokens=2000
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ GPT-4o Vision failed: {e}")
        raise ValueError("GPT could not extract the table from the PDF.")
