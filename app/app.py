import sys
import os
sys.path.append(os.path.abspath(".."))

from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    query = request.args.get("q", "").lower()
    source_filter = request.args.get("source", "")
    keyword_filter = request.args.get("keyword", "")

    google_df = pd.read_csv("../outputs/google_trends.csv")
    news_df = pd.read_csv("../outputs/news_counts.csv")
    amazon_df = pd.read_csv("../outputs/amazon_reviews.csv")

    if query:
        google_df = google_df[google_df["keyword"].str.lower().str.contains(query, na=False)]
        news_df = news_df[news_df["keyword"].str.lower().str.contains(query, na=False)]
        amazon_df = amazon_df[amazon_df["product"].str.lower().str.contains(query, na=False)]

    if source_filter:
        news_df = news_df[news_df["source"] == source_filter]

    if keyword_filter:
        google_df = google_df[google_df["keyword"] == keyword_filter]
        news_df = news_df[news_df["keyword"] == keyword_filter]

    google_records = google_df.to_dict(orient="records")
    news_records = news_df.to_dict(orient="records")
    amazon_records = amazon_df.to_dict(orient="records")

    available_sources = sorted(pd.read_csv("../outputs/news_counts.csv")["source"].dropna().unique())
    available_keywords = sorted(
        set(pd.read_csv("../outputs/google_trends.csv")["keyword"].dropna().unique()).union(
            set(pd.read_csv("../outputs/news_counts.csv")["keyword"].dropna().unique())
        )
    )

    return render_template(
        "index.html",
        google_records=google_records,
        news_records=news_records,
        amazon_records=amazon_records,
        available_sources=available_sources,
        available_keywords=available_keywords,
        query=query,
        source_filter=source_filter,
        keyword_filter=keyword_filter
    )

if __name__ == "__main__":
    app.run(debug=True)
