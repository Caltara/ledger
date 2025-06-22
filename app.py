from pdf_parser import extract_tables_from_pdf  # the new GPT version

if uploaded_file:
    try:
        with st.spinner("Processing file..."):
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

            anomalies = detect_irregularities(df)

            st.subheader("🚨 Detected Irregularities")
            if anomalies:
                st.table(pd.DataFrame(anomalies))
            else:
                st.success("No significant irregularities found.")

            # Your plotting code here...

    except ValueError as ve:
        st.error(f"❌ {str(ve)}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {str(e)}")
