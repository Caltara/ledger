import pandas as pd
from io import StringIO
import fitz  # PyMuPDF
import openai

def extract_tables_from_pdf(uploaded_file):
    try:
        # Extract text from all pages using PyMuPDF
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n"

        if not all_text.strip():
            raise ValueError("No extractable text found in PDF.")

        # Call OpenAI GPT-4o Vision to extract tables as JSON object
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial data analyst. "
                        "Extract tables from this Profit & Loss statement text and return the data as a JSON object "
                        "with column headers matching line items and date columns."
                    ),
                },
                {"role": "user", "content": all_text},
            ],
            response_format={"type": "json_object"},
        )

        extracted_json_obj = response.choices[0].message.content
        
        # The content is already a Python dict (not a JSON string), so convert it directly to DataFrame
        df = pd.DataFrame(extracted_json_obj)
        return df

    except Exception as e:
        raise ValueError(
            "❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
