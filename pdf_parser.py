import pandas as pd
import fitz  # PyMuPDF
import openai

def extract_tables_from_pdf(uploaded_file):
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n"

        if not all_text.strip():
            raise ValueError("No extractable text found in PDF.")

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

        extracted_obj = response.choices[0].message.content

        # Handle nested data if present
        if isinstance(extracted_obj, dict) and "data" in extracted_obj:
            data_for_df = extracted_obj["data"]
        else:
            data_for_df = extracted_obj

        df = pd.DataFrame(data_for_df)

        if df.empty:
            raise ValueError("Extracted data is empty.")

        return df

    except Exception as e:
        raise ValueError(
            "❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
