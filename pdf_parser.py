import openai
import fitz  # PyMuPDF
import pandas as pd
import json

def extract_tables_from_pdf(file):
    try:
        # Read the PDF text
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            all_text = "\n".join([page.get_text() for page in doc])

        # Ask GPT to extract the table
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the Profit & Loss table from this PDF text. "
                        "Return only a JSON array of dictionaries — one per row — no extra explanation."
                    )
                },
                {"role": "user", "content": all_text}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ GPT returned invalid JSON: {e}")

        # Case 1: Raw JSON array
        if isinstance(parsed, list):
            return pd.DataFrame(parsed)

        # Case 2: Dict with a table-like key
        for key in ["table", "rows", "data"]:
            if key in parsed and isinstance(parsed[key], list):
                return pd.DataFrame(parsed[key])

        # If none of the above worked:
        raise ValueError("❌ GPT response did not include a recognizable table key or valid array.")

    except Exception as e:
        raise ValueError(f"❌ GPT failed to extract table from PDF. Error: {str(e)}")
