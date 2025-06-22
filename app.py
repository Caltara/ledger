import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities
from pdf_parser import extract_tables_from_pdf

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in CSV or PDF format.  
- CSV: From Excel or QuickBooks exports  
- PDF: GPT-powered extraction for complex structured reports
""")

uploaded_file = st.file_uploader("📤 Upload CSV or PDF", type=["csv", "pdf"])

if uploaded_file:
    try:
        with st.spinner("🔍 Processing file..."):
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                raw_df = extract_tables_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            st.subheader("📑 Raw Extracted Data Preview (First 10 rows)")
            st.dataframe(raw_df.head(10))

            df = clean_and_convert(raw_df)

            st.subheader("📊 Cleaned P&L Table Preview (First 10 rows)")
            st.dataframe(df.head(10))

            anomalies = detect_irregularities(df)

            st.subheader("🚨 Detected Irregularities (±5% Changes)")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("✅ No significant irregularities found.")

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
