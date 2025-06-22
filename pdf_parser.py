import openai
import fitz  # PyMuPDF
import pandas as pd
import json

def extract_tables_from_pdf(file):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            all_text = "\n".join([page.get_text() for page in doc])

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You're a financial data analyst. Extract the Profit & Loss table from the following text. "
                        "Return ONLY a JSON array of dictionaries. Each dictionary should include:"
                        " 'Line Item', date-based revenue columns, and any percentage change columns. "
                        "Do not wrap it in an object. Do not include explanations."
                    )
                },
                {"role": "user", "content": all_text}
            ],
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            raise ValueError("GPT returned invalid JSON.")

        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)
        elif isinstance(parsed, dict):
            for key in ["table", "data", "rows", "result", "lines"]:
                if key in parsed and isinstance(parsed[key], list):
                    df = pd.DataFrame(parsed[key])
                    break
            else:
                raise ValueError("GPT response did not include a recognizable table key.")
        else:
            raise ValueError("GPT response is not a valid table structure.")

        return df

    except Exception as e:
        raise ValueError(f"❌ GPT failed to extract table from PDF. Error: {str(e)}")
