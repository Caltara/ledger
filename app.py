import streamlit as st
import pandas as pd
from analyzer import clean_and_convert, detect_irregularities, format_for_report, generate_summary
from pdf_parser import extract_tables_from_pdf
from io import StringIO

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a **Profit & Loss (P&L) statement** as a PDF or CSV.  
The app will analyze the full document and provide:
- A high-level summary of your P&L
- A filtered table showing only line items with **±5% or more change**
""")

uploaded_file = st.file_uploader("📤 Upload CSV or PDF", type=["csv", "pdf"])

if uploaded_file:
    try:
        with st.spinner("🔍 Scanning and analyzing full P&L..."):
            # Step 1: Extract the full P&L
            if uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                raw_df = extract_tables_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            # Step 2: Clean data for analysis
            cleaned_df = clean_and_convert(raw_df)

            # Step 3: Filter for rows with ±5% change
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

            # Step 4: Show summary
            st.subheader("🧾 P&L Summary")
            st.info(generate_summary(raw_df))

            if not filtered_rows:
                st.success("✅ No significant changes (±5%) found in this P&L.")
                st.stop()

            # Step 5: Format filtered rows for output
            filtered_df = pd.DataFrame(filtered_rows)
            formatted_df = format_for_report(clean_and_convert(filtered_df))

            st.subheader("📌 Significant Line Item Changes (±5%)")
            st.dataframe(formatted_df, use_container_width=True)

            # Step 6: Download button
            csv_buffer = StringIO()
            formatted_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Filtered Report (CSV)",
                data=csv_buffer.getvalue(),
                file_name="significant_changes.csv",
                mime="text/csv"
            )

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
