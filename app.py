import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from analyzer import clean_and_convert, detect_irregularities
from pdf_parser import extract_tables_from_pdf, extract_ocr_text

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in either CSV or PDF format.  
- CSV: Must have line items in the first column and numbers in the rest  
- PDF: Can be scanned or digital, we'll try OCR if tables can't be found
""")

# ✅ Optional: CSV Template Download
sample_csv = """Line Item,Jan 2025,Feb 2025,Mar 2025,Apr 2025
Revenue,$12,000,$11,500,$13,000,$12,500
Cost of Goods Sold,$4,000,$3,900,$4,200,$4,100
Gross Profit,$8,000,$7,600,$8,800,$8,400
Operating Expenses,$3,000,$3,200,$3,100,$3,050
Net Income,$5,000,$4,400,$5,700,$5,350
"""
st.download_button("📥 Download Sample CSV Template", sample_csv, file_name="pnl_template.csv", mime="text/csv")

# 📤 File Upload
uploaded_file = st.file_uploader("Upload your P&L (CSV or PDF)", type=["csv", "pdf"])

if uploaded_file:
    try:
        with st.spinner("Processing file..."):

            # ✅ CSV File Upload
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)

            # ✅ PDF File Upload
            elif uploaded_file.type == "application/pdf":
                try:
                    raw_df = extract_tables_from_pdf(uploaded_file)
                except Exception as e:
                    st.warning("⚠️ Table parsing failed. Showing raw OCR text for review.")
                    uploaded_file.seek(0)
                    ocr_text = extract_ocr_text(uploaded_file)
                    st.text_area("📄 OCR Output (Unstructured Text)", ocr_text, height=400)
                    st.stop()

            else:
                st.error("Unsupported file type.")
                st.stop()

            # ✅ Data Preview
            st.subheader("📑 Raw Extracted Data")
            st.dataframe(raw_df)

            # ✅ Clean and Analyze
            df = clean_and_convert(raw_df)

            st.subheader("📊 Cleaned P&L Table")
            st.dataframe(df)

            anomalies = detect_irregularities(df)

            st.subheader("🚨 Detected Irregularities")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("No significant irregularities found.")

            st.subheader("📈 Trend Visualization")
            plt.figure(figsize=(10, 6))
            for i in range(len(df)):
                plt.plot(df.columns[1:], df.iloc[i, 1:], label=df.iloc[i, 0])
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
