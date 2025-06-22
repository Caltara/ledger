import io
import pandas as pd
from pdf2image import convert_from_bytes
from PIL import Image
import openai
import streamlit as st

# Initialize OpenAI client with API key from Streamlit secrets or environment
openai.api_key = st.secrets.get("OPENAI_API_KEY") or ""

def extract_tables_from_pdf(file) -> pd.DataFrame:
    """
    Convert PDF pages to images, send each image to GPT-4 Vision,
    parse GPT response JSON table and combine into one DataFrame.
    """
    file.seek(0)
    images = convert_from_bytes(file.read())

    all_dfs = []
    for i, image in enumerate(images):
        st.info(f"Processing page {i+1} with GPT-4 Vision...")
        table_df = gpt_extract_table_from_image(image)
        if table_df is not None:
            all_dfs.append(table_df)

    if not all_dfs:
        raise ValueError("GPT-4 Vision could not extract any table data from the PDF.")

    return pd.concat(all_dfs, ignore_index=True)


def gpt_extract_table_from_image(image: Image.Image) -> pd.DataFrame | None:
    """
    Send image to GPT-4 Vision with prompt to extract P&L table as JSON.
    Returns a DataFrame or None if extraction fails.
    """

    # Convert PIL Image to bytes
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    # Craft system and user prompt
    system_prompt = (
        "You are an expert financial analyst. "
        "Extract the Profit & Loss statement table from the image and "
        "return the data as JSON in this format:\n"
        '[{"Line Item": "Revenue", "Jan 2025": 12000, "Feb 2025": 11500, ...}, {...}]\n'
        "Ensure numbers are plain integers or floats without currency symbols or commas."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Extract the table from this image."}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            modalities=["image"],
            inputs=[{"type": "image", "image": img_bytes}],
            temperature=0,
            max_tokens=1500,
        )
        text_response = response.choices[0].message.content.strip()

        # Parse JSON text to DataFrame
        df = pd.read_json(text_response)
        return df

    except Exception as e:
        st.error(f"GPT extraction error: {e}")
        return None
