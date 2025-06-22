import pandas as pd
import fitz  # PyMuPDF
import openai

def extract_tables_from_pdf(uploaded_file):
    """
    Extract tables from a PDF file by reading all text and
    sending it to GPT-4o Vision to extract tabular data as JSON.

    Args:
        uploaded_file: A file-like object (from Streamlit uploader)

    Returns:
        pandas.DataFrame containing the extracted table data

    Raises:
        ValueError if extraction fails or data format is unexpected
    """
    try:
        # Extract text from all pages in the PDF
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n"

        if not all_text.strip():
            raise ValueError("No extractable text found in PDF.")

        # Call OpenAI GPT-4o Vision API to parse the P&L table as JSON object
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

        # DEBUG: Uncomment to inspect raw GPT output if needed
        # print("Extracted GPT JSON object:", extracted_obj)

        # Extract the actual table data from the response
        if isinstance(extracted_obj, dict):
            # If the response wraps data inside a key, update here accordingly
            if "data" in extracted_obj:
                data_for_df = extracted_obj["data"]
            else:
                data_for_df = extracted_obj
        else:
            data_for_df = extracted_obj

        # Convert extracted data to pandas DataFrame
        df = pd.DataFrame(data_for_df)

        if df.empty:
            raise ValueError("Extracted data is empty.")

        return df

    except Exception as e:
        raise ValueError(
            "❌ GPT failed to extract table from PDF. Make sure it's a readable P&L export. Error: "
            + str(e)
        )
