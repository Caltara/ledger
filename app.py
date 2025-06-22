import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analyzer import clean_and_convert, detect_irregularities

st.set_page_config(page_title="Ledger | P&L Analyzer", layout="wide")
st.title("📊 Ledger | P&L Analyzer")

st.markdown("""
Upload a clean Profit & Loss (P&L) statement in CSV format.  
Make sure it includes numeric values only (no formulas or text), and that currency symbols or commas are allowed but not required.
""")

# Optional: download button for template
sample_csv = """Line Item,Jan 2025,Feb 2025,Mar 2025,Apr 2025
Revenue,$12,000,$11,500,$13,000,$12,500
Cost of Goods Sold,$4,000,$3,900,$4,200,$4,100
Gross Profit,$8,000,$7,600,$8,800,$8,400
Operating Expenses,$3,000,$3,200,$3,100,$3,050
Net Income,$5,000,$4,400,$5,700,$5,350
"""
st.download_button("📥 Download Sample CSV Template", sample_csv, file_name="pnl_template.csv", mime="text/csv")

# Upload P&L CSV
uploaded_file = st.file_uploader("Upload your P&L statement (CSV only)", type=["csv"])

if uploaded_file:
    try:
        with st.spinner("Analyzing P&L..."):
            raw_df = pd.read_csv(uploaded_file)
            st.subheader("🔍 Raw Uploaded Data")
            st.dataframe(raw_df)

            df = clean_and_convert(raw_df)

            st.subheader("📑 Cleaned P&L Data")
            st.dataframe(df)

            anomalies = detect_irregularities(df)

            st.subheader("📍 Detected Irregularities")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("No significant irregularities found!")

            st.subheader("📈 Trend Visualization")
            plt.figure(figsize=(10, 6))
            for i in range(len(df)):
                plt.plot(df.columns[1:], df.iloc[i, 1:], label=df.iloc[i, 0])
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

    except ValueError as e:
        st.error(f"❌ {str(e)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
