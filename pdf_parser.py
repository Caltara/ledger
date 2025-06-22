import openai
import fitz  # PyMuPDF
import pandas as pd
import json

def extract_tables_from_pdf(file):
    try:
        # Extract text from all pages
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            all_text = "\n".join([page.get_text() for page in doc])

        # Ask GPT to extract the table as a JSON array of rows
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial analyst assistant. Extract the Profit & Loss table from the provided report. "
                        "Return ONLY a JSON array of dictionaries. Each dictionary should represent one line item with revenue and percent change columns. "
                        "Do NOT return any explanation or extra text — only a clean JSON array."
                    )
                },
                {"role": "user", "content": all_text}
            ],
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON returned from GPT: {e}")

        # ✅ Fix: Try parsing top-level list first
        if isinstance(parsed, list):
            return pd.DataFrame(parsed)

        # ✅ Otherwise, try to find a table-like key inside a dict
        if isinstance(parsed, dict):
            for key in ["table", "data", "rows", "result", "items", "lines"]:
                if key in parsed and isinstance(parsed[key], list):
                    return pd.DataFrame(parsed[key])

        raise ValueError("❌ GPT response did not include a recognizable table key or valid array.")

    except Exception as e:
        raise ValueError(f"❌ GPT failed to extract table from PDF. Error: {str(e)}")
