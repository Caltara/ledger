import fitz  # PyMuPDF, install with: pip install pymupdf
import io
import base64
import json
import re
import pandas as pd
from openai import OpenAI
import streamlit as st

client = OpenAI()

def convert_pdf_to_images(file) -> list[str]:
    """
    Convert all PDF pages to base64-encoded PNG images as data URLs.
    """
    file.seek(0)  # Ensure start of file
    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
    images_base64 = []
    for page_num in range(pdf_doc.page_count):
        page = pdf_doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images_base64.append(f"data:image/png;base64,{img_b64}")
    return images_base64

def extract_json(text: str) -> str:
    """
    Extract the longest JSON array from GPT raw response text.
    """
    matches = re.findall(r'(\[.*\])', text, re.DOTALL)
    if not matches:
        return text
    longest = max(matches, key=len)
    return longest

def extract_tables_from_pdf(file) -> pd.DataFrame:
    """
    Extract P&L tables from all pages of a PDF using GPT-4o Vision.

    Args:
        file: Uploaded PDF file-like object.

    Returns:
        Combined pandas DataFrame with all extracted data.
    """

    st.info("Converting PDF pages to images...")
    images = convert_pdf_to_images(file)

    all_dfs = []

    for i, img_url in enumerate(images):
        st.info(f"Processing page {i+1} of {len(images)} with GPT...")

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant specialized in extracting financial data. "
                            "Extract ONLY the Profit & Loss table from the provided image. "
                            "Output ONLY a valid JSON array of objects, where keys are column headers and values are the row data. "
                            "DO NOT include any explanation, markdown, or extra text."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract the P&L table from the image below as JSON ONLY."},
                            {"type": "image_url", "image_url": {"url": img_url, "alt_text": f"Page {i+1} of PDF"}}
                        ]
                    }
                ],
                max_tokens=2000
            )

            raw = response.choices[0].message.content
            st.code(f"Raw GPT response for page {i+1}:\n{raw}")

            json_text = extract_json(raw)

            data = json.loads(json_text)
            df_page = pd.DataFrame(data)
            all_dfs.append(df_page)

        except json.JSONDecodeError:
            st.error(f"❌ Failed to parse JSON from GPT response on page {i+1}. Please check your PDF content.")
        except Exception as e:
            st.error(f"❌ Unexpected error on page {i+1}: {str(e)}")

    if not all_dfs:
        raise ValueError("No tables extracted from any PDF pages.")

    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df
