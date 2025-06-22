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
                        "You are a financial data analyst. Extract the Profit & Loss table data from this text. "
                        "Return a JSON array of dictionaries, where each dictionary is one row of the table. "
                        "Each dictionary should have column headers like 'Line Item', dates, and % changes."
                    ),
                },
                {"role": "user", "content": all_text},
            ],
            response_format={"type": "json_object"},
        )

        extracted_obj = response.choices[0].message.content

        # Ensure content is parsed
        if isinstance(extracted_obj, str):
            import json
            extracted_obj = json.loads(extracted_obj)

        # ✅ FIX: if GPT wraps it inside {"table": [...]}, unwrap it
        if isinstance(extracted_obj, dict):
            if "table" in extracted_obj:
                data_for_df = extracted_obj["table"]
            elif "data" in extracted_obj:
                data_for_df = extracted_obj["data"]
            else:
                raise ValueError("GPT response did not include a valid table key.")
        elif isinstance(extracted_obj, list):
            data_for_df = extracted_obj
        else:
            raise ValueError("GPT response is not a valid JSON list or object.")

        df = pd.DataFrame(data_for_df)

        if df.empty:
            raise ValueError("Extracted data is empty.")

        return df

    except Exception as e:
        raise ValueError(
            "❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
