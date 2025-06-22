import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities
from pdf_parser import extract_tables_from_pdf

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in CSV or PDF format.  
- CSV: From Excel or QuickBooks  
- PDF: GPT-4o Vision will extract tables from images of your PDF  
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

            st.subheader("📑 Raw Extracted Data")
            st.dataframe(raw_df)

            df = clean_and_convert(raw_df)

            st.subheader("📊 Cleaned P&L Table")
            st.dataframe(df)

            anomalies = detect_irregularities(df, threshold_pct=0.3)

            st.subheader("🚨 Detected Irregularities")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("✅ No significant irregularities found.")

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
