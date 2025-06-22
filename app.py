import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pdf_parser import extract_tables_from_pdf
from analyzer import clean_and_convert, detect_irregularities

st.set_page_config(page_title="AI P&L Analyzer", layout="wide")
st.title("📊 AI P&L Analyzer")

uploaded_file = st.file_uploader(
    "Upload your P&L statement (PDF or CSV)", 
    type=["pdf", "csv"]
)

if uploaded_file:
    try:
        with st.spinner("Extracting and analyzing..."):

            if uploaded_file.type == "application/pdf":
                raw_df = extract_tables_from_pdf(uploaded_file)
            elif uploaded_file.type == "text/csv":
                raw_df = pd.read_csv(uploaded_file)
            else:
                st.error("Unsupported file type.")
                st.stop()

            df = clean_and_convert(raw_df)

            st.subheader("Parsed P&L Data")
            st.dataframe(df)

            anomalies = detect_irregularities(df)

            st.subheader("📍 Detected Irregularities")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("No significant irregularities found!")

            st.subheader("📈 Visual Summary")
            plt.figure(figsize=(10, 6))
            for i in range(len(df)):
                plt.plot(df.columns[1:], df.iloc[i, 1:], label=df.iloc[i, 0])
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt)

    except ValueError as e:
        st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
