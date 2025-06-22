import pandas as pd
import fitz  # PyMuPDF
import openai
import json

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
                        "You're a financial data analyst. Extract the Profit & Loss table from this text. "
                        "Return ONLY a JSON array of rows — do not wrap it in an object. Each row should include "
                        "'Line Item', date columns, and % change columns."
                    ),
                },
                {"role": "user", "content": all_text},
            ],
            response_format={"type": "json_object"},
        )

        raw_json = response.choices[0].message.content

        if isinstance(raw_json, str):
            parsed = json.loads(raw_json)
        else:
            parsed = raw_json

        # Case 1: Direct list (ideal)
        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)

        # Case 2: Wrapped in dict — try to auto-detect key
        elif isinstance(parsed, dict):
            possible_keys = ["table", "data", "rows", "result", "lines"]
            for key in possible_keys:
                if key in parsed and isinstance(parsed[key], list):
                    df = pd.DataFrame(parsed[key])
                    break
            else:
                raise ValueError("GPT response did not include a recognizable table key.")

        else:
            raise ValueError("Invalid GPT JSON response format.")

        if df.empty:
            raise ValueError("Extracted table is empty.")

        return df

    except Exception as e:
        raise ValueError(
            "❌ ❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
