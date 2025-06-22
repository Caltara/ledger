import pandas as pd
from io import StringIO
import fitz  # PyMuPDF
import openai

def extract_tables_from_pdf(uploaded_file):
    try:
        # Read PDF pages text with PyMuPDF
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n"

        if not all_text.strip():
            raise ValueError("No extractable text found in PDF.")

        # Call OpenAI GPT-4o Vision to extract tables as JSON
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial data analyst. "
                        "Extract tables from this Profit & Loss statement text and return the data as JSON array "
                        "with column headers matching line items and date columns."
                    ),
                },
                {"role": "user", "content": all_text},
            ],
            response_format={"type": "json"},  # Correct format here
        )

        # Parse JSON string to DataFrame
        extracted_json = response.choices[0].message.content
        df = pd.read_json(StringIO(extracted_json))
        return df

    except Exception as e:
        raise ValueError(
            "❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
