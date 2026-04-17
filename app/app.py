from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

@app.route("/")
def home():
    query = request.args.get("q", "").lower()
    source_filter = request.args.get("source", "")
    keyword_filter = request.args.get("keyword", "")

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))

    google_df = pd.read_csv(os.path.join(base_path, "google_trends.csv"))
    news_df = pd.read_csv(os.path.join(base_path, "news_counts.csv"))
    amazon_df = pd.read_csv(os.path.join(base_path, "amazon_reviews.csv"))

    if query:
        google_df = google_df[google_df["keyword"].astype(str).str.lower().str.contains(query, na=False)]
        news_df = news_df[news_df["keyword"].astype(str).str.lower().str.contains(query, na=False)]
        amazon_df = amazon_df[amazon_df["product"].astype(str).str.lower().str.contains(query, na=False)]

    if source_filter:
        news_df = news_df[news_df["source"] == source_filter]

    if keyword_filter:
        google_df = google_df[google_df["keyword"] == keyword_filter]
        news_df = news_df[news_df["keyword"] == keyword_filter]

    google_records = google_df.to_dict(orient="records")
    news_records = news_df.to_dict(orient="records")
    amazon_records = amazon_df.to_dict(orient="records")

    available_sources = sorted(news_df["source"].dropna().astype(str).unique().tolist())

    all_keywords = sorted(
        set(google_df["keyword"].dropna().astype(str).tolist()) |
        set(news_df["keyword"].dropna().astype(str).tolist())
    )

    return render_template(
        "index.html",
        google_records=google_records,
        news_records=news_records,
        amazon_records=amazon_records,
        available_sources=available_sources,
        available_keywords=all_keywords,
        query=query,
        source_filter=source_filter,
        keyword_filter=keyword_filter
    )

if __name__ == "__main__":
    app.run(debug=True)