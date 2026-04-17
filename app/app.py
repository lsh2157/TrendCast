import sys
import os

sys.path.append(os.path.abspath(".."))

from flask import Flask, render_template, request
from data_sources.mongodb.queries import get_latest_news

app = Flask(__name__)

@app.route("/")
def home():
    query = request.args.get("q", "").lower()

    raw_data = get_latest_news(25)

    records = []
    for row in raw_data:
        record = {
            "keyword": row.get("title", "N/A"),
            "trend_score": 50,
            "score_date": row.get("publishedAt", "N/A"),
            "source": row.get("source", "N/A")
        }

        if query:
            if query in record["keyword"].lower():
                records.append(record)
        else:
            records.append(record)

    return render_template("index.html", records=records, query=query)

if __name__ == "__main__":
    app.run(debug=True)