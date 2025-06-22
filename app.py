import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities, format_for_report, generate_summary
from pdf_parser import extract_tables_from_pdf
from io import StringIO

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** in either CSV or PDF format.  
🔍 This tool scans your entire document and shows only the line items that changed by more than **5%**.
""")

uploaded_file = st.file_uploader("📤 Upload CSV or PDF", type=["csv", "pdf"])

if uploaded_file:
    try:
        with st.spinner("🔍 Processing file..."):
            # Step 1: Extract Raw Data
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                raw_df = extract_tables_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            st.subheader("📑 Raw Extracted Data")
            st.dataframe(raw_df)

            # Step 2: Clean for numeric calculations
            cleaned_df = clean_and_convert(raw_df)

            # Step 3: Detect only significant changes
            filtered_rows = []
            for i, row in cleaned_df.iterrows():
                for col in cleaned_df.columns:
                    if "change" in col.lower():
                        try:
                            value = float(row[col])
                            if abs(value) >= 5:
                                filtered_rows.append(raw_df.loc[i])
                                break
                        except:
                            continue

            if not filtered_rows:
                st.success("✅ No line items changed by more than 5%.")
                st.stop()

            # Step 4: Format filtered rows for readability
            filtered_df = pd.DataFrame(filtered_rows)
            formatted_df = format_for_report(clean_and_convert(filtered_df))

            st.subheader("📈 Summary Report (±5% Changes)")
            st.dataframe(formatted_df, use_container_width=True)

            # Step 5: Generate high-level summary
            st.markdown("### 🧾 Overall Summary")
            st.info(generate_summary(filtered_df))

            # Step 6: Download filtered report
            csv_buffer = StringIO()
            formatted_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Filtered Report (CSV)",
                data=csv_buffer.getvalue(),
                file_name="summary_report.csv",
                mime="text/csv"
            )

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
