import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TrendCast Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }

    h1, h2, h3 {
        color: #0f172a;
    }

    .subtitle {
        color: #475569;
        font-size: 1rem;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }

    .section-card {
        background: white;
        padding: 1.2rem 1.2rem 0.8rem 1.2rem;
        border-radius: 16px;
        box-shadow: 0 1px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border: 1px solid #e2e8f0;
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
    }

    .small-note {
        color: #64748b;
        font-size: 0.9rem;
    }

    .headline-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    .headline-title {
        color: #0f172a;
        font-weight: 600;
        font-size: 0.97rem;
        margin-bottom: 0.25rem;
    }

    .headline-meta {
        color: #64748b;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- FILE PATHS ----------------
GOOGLE_TRENDS_FILE = "data/table1_google_trends.csv"
NEWSAPI_COUNTS_FILE = "data/table2_newsapi_keyword_counts.csv"
NYT_COUNTS_FILE = "data/table2_nyt_keyword_counts.csv"
AMAZON_FILE = "data/table3_amazon_reviews.csv"

ATLAS_URI = "mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0"

# ---------------- HELPERS ----------------
@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data(ttl=60)
def load_mongo_headlines():
    client = MongoClient(ATLAS_URI)
    db = client["trendcast"]
    news_docs = list(db["news_articles"].find().limit(100))
    nyt_docs = list(db["nytimes_articles"].find().limit(100))
    client.close()
    return news_docs, nyt_docs

# ---------------- HEADER ----------------
st.title("📊 TrendCast Dashboard")
st.markdown(
    '<div class="subtitle">Electronics market trend monitoring across Google Trends, news sources, and Amazon review data.</div>',
    unsafe_allow_html=True,
)

# ---------------- OVERVIEW METRICS ----------------
try:
    google_df = load_csv(GOOGLE_TRENDS_FILE)
    google_keywords = google_df["keyword"].nunique() if "keyword" in google_df.columns else 0
except Exception:
    google_keywords = 0

try:
    newsapi_df = load_csv(NEWSAPI_COUNTS_FILE)
    newsapi_keywords = newsapi_df["keyword"].nunique() if "keyword" in newsapi_df.columns else 0
except Exception:
    newsapi_keywords = 0

try:
    nyt_counts_df = load_csv(NYT_COUNTS_FILE)
    nyt_keywords = nyt_counts_df["keyword"].nunique() if "keyword" in nyt_counts_df.columns else 0
except Exception:
    nyt_keywords = 0

try:
    amazon_df = load_csv(AMAZON_FILE)
    amazon_categories = amazon_df["main_category"].nunique() if "main_category" in amazon_df.columns else 0
except Exception:
    amazon_categories = 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Google Trend Keywords", google_keywords)
m2.metric("NewsAPI Keywords", newsapi_keywords)
m3.metric("NYT Keywords", nyt_keywords)
m4.metric("Amazon Categories", amazon_categories)

st.markdown("---")

# =========================================================
# GOOGLE TRENDS
# =========================================================
st.header("📈 Google Trends")

try:
    google_df = load_csv(GOOGLE_TRENDS_FILE)

    gfilter1, gfilter2 = st.columns([1, 1])

    with gfilter1:
        google_search = st.text_input("Search Google Trends keyword", "", key="google_search")

    with gfilter2:
        if "keyword" in google_df.columns:
            google_options = ["All"] + sorted(google_df["keyword"].dropna().astype(str).unique().tolist())
            google_selected = st.selectbox("Filter keyword", google_options, key="google_filter")
        else:
            google_selected = "All"

    filtered_google = google_df.copy()

    if "keyword" in filtered_google.columns:
        filtered_google["keyword"] = filtered_google["keyword"].astype(str)
        if google_search:
            filtered_google = filtered_google[
                filtered_google["keyword"].str.contains(google_search, case=False, na=False)
            ]
        if google_selected != "All":
            filtered_google = filtered_google[filtered_google["keyword"] == google_selected]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Keyword Popularity")
        if {"keyword", "counts"}.issubset(filtered_google.columns):
            keyword_df = (
                filtered_google.groupby("keyword", as_index=False)["counts"]
                .sum()
                .sort_values("counts", ascending=False)
                .head(10)
            )
            if not keyword_df.empty:
                st.bar_chart(keyword_df.set_index("keyword"))
            else:
                st.info("No Google Trends rows match the current filters.")
        else:
            st.info("Expected columns 'keyword' and 'counts' were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Trend Over Time")
        if {"date", "counts"}.issubset(filtered_google.columns):
            time_df = filtered_google.copy()
            time_df["date"] = pd.to_datetime(time_df["date"], errors="coerce")
            time_df = (
                time_df.dropna(subset=["date"])
                .groupby("date", as_index=False)["counts"]
                .sum()
                .sort_values("date")
            )
            if not time_df.empty:
                st.line_chart(time_df.set_index("date")["counts"])
            else:
                st.info("No valid date rows found.")
        else:
            st.info("Expected columns 'date' and 'counts' were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("View Google Trends data"):
        st.dataframe(filtered_google, use_container_width=True)

except Exception as e:
    st.error(f"Google Trends data error: {e}")

st.markdown("---")

# =========================================================
# NEWS COUNTS
# =========================================================
st.header("📰 News Trends")

try:
    newsapi_df = load_csv(NEWSAPI_COUNTS_FILE)
    nyt_counts_df = load_csv(NYT_COUNTS_FILE)

    nfilter1, nfilter2 = st.columns(2)

    with nfilter1:
        news_search = st.text_input("Search NewsAPI keyword", "", key="news_search")

    with nfilter2:
        nyt_search = st.text_input("Search NYT keyword", "", key="nyt_search")

    filtered_newsapi = newsapi_df.copy()
    filtered_nyt = nyt_counts_df.copy()

    if {"keyword", "counts"}.issubset(filtered_newsapi.columns):
        filtered_newsapi["keyword"] = filtered_newsapi["keyword"].astype(str)
        if news_search:
            filtered_newsapi = filtered_newsapi[
                filtered_newsapi["keyword"].str.contains(news_search, case=False, na=False)
            ]

    if {"keyword", "counts"}.issubset(filtered_nyt.columns):
        filtered_nyt["keyword"] = filtered_nyt["keyword"].astype(str)
        if nyt_search:
            filtered_nyt = filtered_nyt[
                filtered_nyt["keyword"].str.contains(nyt_search, case=False, na=False)
            ]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("NewsAPI Keyword Counts")
        if {"keyword", "counts"}.issubset(filtered_newsapi.columns):
            chart_df = filtered_newsapi.sort_values("counts", ascending=False).head(10)
            if not chart_df.empty:
                st.bar_chart(chart_df.set_index("keyword")["counts"])
            else:
                st.info("No NewsAPI rows match the current search.")
        else:
            st.info("Expected columns 'keyword' and 'counts' were not found.")

        with st.expander("View NewsAPI table"):
            st.dataframe(filtered_newsapi, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("NYT Keyword Counts")
        if {"keyword", "counts"}.issubset(filtered_nyt.columns):
            chart_df = filtered_nyt.sort_values("counts", ascending=False).head(10)
            if not chart_df.empty:
                st.bar_chart(chart_df.set_index("keyword")["counts"])
            else:
                st.info("No NYT rows match the current search.")
        else:
            st.info("Expected columns 'keyword' and 'counts' were not found.")

        with st.expander("View NYT table"):
            st.dataframe(filtered_nyt, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"News trend data error: {e}")

# =========================================================
# LIVE MONGO HEADLINES
# =========================================================
st.subheader("🗞️ Live Mongo Headlines")

try:
    news_docs, nyt_docs = load_mongo_headlines()

    hfilter1, hfilter2 = st.columns(2)

    with hfilter1:
        mongo_news_search = st.text_input("Search live news headlines", "", key="mongo_news_search")

    with hfilter2:
        mongo_nyt_search = st.text_input("Search live NYT headlines", "", key="mongo_nyt_search")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Latest News Articles")
        seen = set()
        shown = 0

        for article in news_docs:
            title = article.get("title")
            source = article.get("source", "")
            date = article.get("publishedAt", "")

            if not title:
                continue
            if "test" in title.lower():
                continue
            if mongo_news_search and mongo_news_search.lower() not in title.lower():
                continue
            if title in seen:
                continue

            seen.add(title)
            st.markdown(
                f"""
                <div class="headline-box">
                    <div class="headline-title">{title}</div>
                    <div class="headline-meta">{source} {("• " + str(date)) if date else ""}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            shown += 1
            if shown >= 8:
                break

        if shown == 0:
            st.caption("No matching non-test news articles found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Latest NYT Headlines")
        seen = set()
        shown = 0

        for article in nyt_docs:
            title = article.get("headline") or article.get("title")
            date = article.get("pub_date") or article.get("publishedAt", "")

            if not title:
                continue
            if "test headline" in title.lower() or "nyt test" in title.lower():
                continue
            if mongo_nyt_search and mongo_nyt_search.lower() not in title.lower():
                continue
            if title in seen:
                continue

            seen.add(title)
            st.markdown(
                f"""
                <div class="headline-box">
                    <div class="headline-title">{title}</div>
                    <div class="headline-meta">New York Times {("• " + str(date)) if date else ""}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            shown += 1
            if shown >= 8:
                break

        if shown == 0:
            st.caption("No matching non-test NYT headlines found.")
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"MongoDB error: {e}")

st.markdown("---")

# =========================================================
# AMAZON
# =========================================================
st.header("🛍️ Product Insights (Amazon Reviews)")

try:
    amazon_df = load_csv(AMAZON_FILE)

    afilter1, afilter2 = st.columns([1, 1])

    with afilter1:
        amazon_search = st.text_input("Search Amazon category", "", key="amazon_search")

    with afilter2:
        if "main_category" in amazon_df.columns:
            category_options = ["All"] + sorted(amazon_df["main_category"].dropna().astype(str).unique().tolist())
            selected_category = st.selectbox("Filter category", category_options, key="amazon_filter")
        else:
            selected_category = "All"

    filtered_amazon = amazon_df.copy()

    if "main_category" in filtered_amazon.columns:
        filtered_amazon["main_category"] = filtered_amazon["main_category"].astype(str)

        if amazon_search:
            filtered_amazon = filtered_amazon[
                filtered_amazon["main_category"].str.contains(amazon_search, case=False, na=False)
            ]

        if selected_category != "All":
            filtered_amazon = filtered_amazon[filtered_amazon["main_category"] == selected_category]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top Categories by Total Reviews")
        if {"main_category", "total_reviews"}.issubset(filtered_amazon.columns):
            amazon_chart = filtered_amazon.sort_values("total_reviews", ascending=False).head(10)
            if not amazon_chart.empty:
                st.bar_chart(amazon_chart.set_index("main_category")["total_reviews"])
            else:
                st.info("No Amazon rows match the current filters.")
        else:
            st.info("Expected columns 'main_category' and 'total_reviews' were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Amazon Review Summary")
        if "total_reviews" in filtered_amazon.columns:
            st.dataframe(
                filtered_amazon.sort_values("total_reviews", ascending=False),
                use_container_width=True,
            )
        else:
            st.dataframe(filtered_amazon, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Amazon data error: {e}")