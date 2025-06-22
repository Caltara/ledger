import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities
from pdf_parser import extract_tables_from_pdf

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

debug_mode = st.checkbox("🔍 Show raw extracted data (debug)", value=False)

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in CSV or PDF format.  
- CSV: Excel or QuickBooks export  
- PDF: Structured or unstructured, GPT tries to extract table.
""")

uploaded_file = st.file_uploader("📤 Upload CSV or PDF", type=["csv", "pdf"])

if uploaded_file:
    try:
        with st.spinner("🔍 Processing file..."):
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
                raw_json = None
            elif uploaded_file.type == "application/pdf":
                raw_df, raw_json = extract_tables_from_pdf(uploaded_file, debug=debug_mode)
            else:
                st.error("Unsupported file type.")
                st.stop()

            if debug_mode and raw_json:
                st.subheader("📑 Raw Extracted Data (JSON from GPT)")
                st.code(raw_json, language="json")

            df = clean_and_convert(raw_df)

            st.subheader("📊 Cleaned P&L Table")
            st.dataframe(df)

            anomalies = detect_irregularities(df)

            st.subheader("🚨 Detected Irregularities (±5% changes)")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("✅ No significant irregularities found.")

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
