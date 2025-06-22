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

        pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
        first_page = pdf_doc.load_page(0)
        pix = first_page.get_pixmap(dpi=200)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_url = f"data:image/png;base64,{img_base64}"

        st.info("Sending image to GPT-4o...")

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise financial analyst. Extract the Profit & Loss statement table from this image. "
                        "ONLY return a JSON array of objects representing rows with columns as keys. "
                        "NO extra explanation or text. Keys should be like 'Line Item', 'Jan', 'Feb', etc."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the P&L table from this image as JSON only."},
                        {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                    ]
                }
            ],
            max_tokens=2000
        )

        raw = response.choices[0].message.content
        st.code("Raw GPT response:\n" + raw)

        data = json.loads(raw)
        return pd.DataFrame(data)

    except json.JSONDecodeError:
        st.error("❌ Failed to parse JSON from GPT response. See raw output above.")
        raise ValueError("GPT returned invalid JSON.")
    except Exception as e:
        st.error(f"❌ GPT-4o Vision failed: {e}")
        raise ValueError("GPT could not extract the table from the PDF.")
