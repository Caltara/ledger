import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities
from pdf_parser import extract_tables_from_pdf

st.set_page_config(page_title="📊 Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in CSV or PDF format.  
This app will summarize totals and highlight line items with a **±5% change**.
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

            df = clean_and_convert(raw_df)
            anomalies = detect_irregularities(df)

            st.subheader("📋 High-Level Summary")
            st.dataframe(df.style.format({"$": "${:,.2f}", "%": "{:+.2f}%"}), use_container_width=True)

            st.subheader("🚨 Line Items with ±5% Change")
            if not anomalies.empty:
                st.dataframe(anomalies.style.format({"$": "${:,.2f}", "%": "{:+.2f}%"}), use_container_width=True)
            else:
                st.success("✅ No significant changes (±5%) found.")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
