import streamlit as st
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="ReviewPulse Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ReviewPulse Analytics")
st.subheader("Customer Review Insights Engine")

# Sentiment Analysis Function
def analyze_sentiment(text):
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

# Input Mode Selection
option = st.radio("Choose Input Method:", ("Enter Text Reviews", "Upload CSV File"))

reviews_list = []

if option == "Enter Text Reviews":
    user_input = st.text_area(
        "Enter reviews (one per line):", 
        value="The product quality is amazing and delivery was super fast!\nWorst purchase ever. Item arrived damaged and customer support was bad.\nLoved the packaging! Great value for money."
    )
    if user_input:
        reviews_list = [line.strip() for line in user_input.split("\n") if line.strip()]

elif option == "Upload CSV File":
    uploaded_file = st.file_uploader("Upload CSV (must contain a column named 'Review Text' or 'review'):", type=["csv"])
    if uploaded_file is not None:
        try:
            # Robust CSV reading to handle parsing errors & bad lines
            try:
                df_uploaded = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='utf-8')
            except Exception:
                df_uploaded = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='latin1')

            col_name = None
            for col in df_uploaded.columns:
                if "review" in col.lower() or "text" in col.lower():
                    col_name = col
                    break
            
            if col_name:
                reviews_list = df_uploaded[col_name].dropna().tolist()
            else:
                st.error("Could not find a review column in the uploaded CSV. Please make sure your CSV has a column like 'Review Text' or 'review'.")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

# Run Analysis
if reviews_list:
    results = []
    for rev in reviews_list:
        sentiment, polarity = analyze_sentiment(rev)
        results.append({
            "Review Text": rev,
            "Sentiment": sentiment,
            "Polarity": round(polarity, 2)
        })
    
    df_results = pd.DataFrame(results)

    # Top Metrics
    total = len(df_results)
    pos_count = len(df_results[df_results["Sentiment"] == "Positive"])
    neg_count = len(df_results[df_results["Sentiment"] == "Negative"])
    neu_count = len(df_results[df_results["Sentiment"] == "Neutral"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews", total)
    col2.metric("Positive 😊", f"{pos_count} ({round(pos_count/total*100, 1)}%)")
    col3.metric("Negative 😡", f"{neg_count} ({round(neg_count/total*100, 1)}%)")
    col4.metric("Neutral 😐", f"{neu_count} ({round(neu_count/total*100, 1)}%)")

    st.markdown("---")

    # Visualizations Section
    col_chart, col_cloud = st.columns(2)

    with col_chart:
        st.subheader("Sentiment Distribution")
        fig = px.pie(
            df_results, 
            names="Sentiment", 
            color="Sentiment",
            color_discrete_map={"Positive": "#2ecc71", "Negative": "#e74c3c", "Neutral": "#95a5a6"},
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_cloud:
        st.subheader("Word Cloud")
        all_text = " ".join(df_results["Review Text"].astype(str).tolist())
        if all_text.strip():
            wordcloud = WordCloud(width=600, height=400, background_color="white").generate(all_text)
            fig_wc, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig_wc)

    st.markdown("---")

    # Filter & Export Section
    st.subheader("Detailed Sentiment Data")
    filter_option = st.selectbox("Filter by Sentiment:", ["All", "Positive", "Negative", "Neutral"])
    
    if filter_option != "All":
        filtered_df = df_results[df_results["Sentiment"] == filter_option]
    else:
        filtered_df = df_results

    st.dataframe(filtered_df, use_container_width=True)

    # Download Button
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Data as CSV",
        data=csv_data,
        file_name="review_sentiment_analysis.csv",
        mime="text/csv"
    )
