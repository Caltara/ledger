import openai
import fitz  # PyMuPDF
import pandas as pd
import json

def extract_tables_from_pdf(file, debug=False):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            all_text = "\n".join([page.get_text() for page in doc])

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial assistant. Extract the Profit & Loss table from the input as a JSON array of rows. "
                        "Each row should be a dictionary with keys like 'Line Item', revenues, percentage changes, etc. "
                        "Return only the JSON array — no explanations or extra formatting."
                    )
                },
                {"role": "user", "content": all_text}
            ],
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content.strip()

        if debug:
            print("📤 GPT Raw Output:\n", raw[:1000])

        parsed = json.loads(raw)

        # Accept raw array
        if isinstance(parsed, list):
            return pd.DataFrame(parsed), raw

        # Accept wrapped object
        for key in ["table", "rows", "data"]:
            if key in parsed and isinstance(parsed[key], list):
                return pd.DataFrame(parsed[key]), raw

        raise ValueError("GPT response did not include a recognizable table key or valid array.")

    except Exception as e:
        raise ValueError(f"GPT failed to extract table from PDF. Error: {str(e)}")
