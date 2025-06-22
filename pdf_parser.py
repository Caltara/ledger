import openai
import fitz  # PyMuPDF
import pandas as pd
import json
import re

def extract_tables_from_pdf(file):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            all_text = "\n".join([page.get_text() for page in doc])

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You're a finance assistant. Extract a full Profit & Loss table as a JSON array of dictionaries. Each row is a line item with values and % change. Return ONLY the array."
                },
                {"role": "user", "content": all_text}
            ]
        )

        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()

        parsed = json.loads(content)
        if isinstance(parsed, list):
            return pd.DataFrame(parsed)

        for key in ["table", "data", "rows"]:
            if key in parsed and isinstance(parsed[key], list):
                return pd.DataFrame(parsed[key])

        raise ValueError("GPT response did not contain a valid table.")
    except Exception as e:
        raise ValueError(f"GPT failed to extract table from PDF. Error: {str(e)}")
