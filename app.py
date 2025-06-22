import streamlit as st
import pandas as pd
from pdf_parser import extract_tables_from_pdf
from analyzer import clean_and_convert, detect_irregularities
import matplotlib.pyplot as plt

st.title("📊 Ledger | P&L Analyzer")

uploaded_file = st.file_uploader("Upload your P&L statement (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Extracting and analyzing..."):
        raw_df = extract_tables_from_pdf(uploaded_file)
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
        for i in range(1, len(df.columns)):
            plt.plot(df.columns[1:], df.iloc[i-1, 1:], label=df.iloc[i-1, 0])
        plt.legend()
        plt.xticks(rotation=45)
        st.pyplot(plt)
