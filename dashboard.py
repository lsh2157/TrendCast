import streamlit as st
import pandas as pd
from pymongo import MongoClient

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TrendCast Dashboard",
    page_icon=None,
    layout="wide"
)

# ---------------- CUSTOM STYLES ----------------
st.markdown(
    """
    <style>
    /* ── Smooth scrolling ── */
    html {
        scroll-behavior: smooth;
    }

    /* ── Import Georgia-like serif stack + Calibri-like sans ── */
    /* Georgia is a system font; Calibri falls back to Trebuchet/sans */

    /* ── Page background ── */
    .main {
        background-color: #EEF4FB;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1350px;
    }

    /* ── Headings: Georgia serif, Columbia Navy ── */
    h1 {
        font-family: Georgia, 'Times New Roman', serif !important;
        color: #002147 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
        letter-spacing: -0.01em;
    }

    h2 {
        font-family: Georgia, 'Times New Roman', serif !important;
        color: #002147 !important;
        font-size: 1.45rem !important;
        font-weight: bold !important;
        border-left: 4px solid #75AADB;
        padding-left: 0.6rem;
        margin-top: 0.5rem !important;
    }

    h3 {
        font-family: Georgia, 'Times New Roman', serif !important;
        color: #002147 !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    /* ── Body text: Calibri / Trebuchet stack ── */
    body, p, div, span, label, input, select, textarea,
    .stMarkdown, .stText {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
        color: #1A1A2E;
    }

    /* ── Subtitle ── */
    .subtitle {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif;
        color: #64748B;
        font-size: 1rem;
        margin-top: -0.4rem;
        margin-bottom: 1.5rem;
    }

    /* ── Section cards ── */
    .section-card {
        background: #FFFFFF;
        padding: 1.4rem 1.4rem 1rem 1.4rem;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 33, 71, 0.07);
        margin-bottom: 1.2rem;
        border: 1px solid #B9D4F1;
    }

    /* ── Headline boxes (MongoDB articles) ── */
    .headline-box {
        background: #FFFFFF;
        border: 1px solid #B9D4F1;
        border-left: 4px solid #75AADB;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.55rem;
        transition: box-shadow 0.2s ease;
    }

    .headline-box:hover {
        box-shadow: 0 4px 14px rgba(0, 33, 71, 0.10);
    }

    .headline-title {
        font-family: Georgia, 'Times New Roman', serif;
        color: #002147;
        font-weight: bold;
        font-size: 0.95rem;
        margin-bottom: 0.2rem;
    }

    .headline-meta {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif;
        color: #64748B;
        font-size: 0.82rem;
    }

    /* ── KPI metric cards ── */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #B9D4F1;
        border-top: 3px solid #002147;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 33, 71, 0.06);
    }

    [data-testid="metric-container"] label {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: bold !important;
        letter-spacing: 0.08em !important;
        color: #64748B !important;
        text-transform: uppercase;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: Georgia, 'Times New Roman', serif !important;
        font-size: 2rem !important;
        color: #002147 !important;
        font-weight: bold !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #002147 !important;
    }

    [data-testid="stSidebar"] * {
        color: #B9D4F1 !important;
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
    }

    /* ── Input fields ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
        border: 1px solid #B9D4F1 !important;
        border-radius: 6px !important;
        background: #FFFFFF !important;
        color: #002147 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #75AADB !important;
        box-shadow: 0 0 0 2px rgba(117, 170, 219, 0.25) !important;
    }

    /* ── Horizontal rule ── */
    hr {
        border: none;
        border-top: 1px solid #B9D4F1;
        margin: 1.5rem 0;
    }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid #B9D4F1 !important;
        border-radius: 6px !important;
        background: #FFFFFF;
    }

    [data-testid="stExpander"] summary {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
        font-weight: bold;
        color: #002147 !important;
    }

    /* ── Dataframe / table ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #B9D4F1;
        border-radius: 6px;
    }

    /* ── Charts: override default blue to Columbia Blue ── */
    [data-testid="stVegaLiteChart"] canvas,
    [data-testid="stArrowVegaLiteChart"] canvas {
        border-radius: 6px;
    }

    /* ── Info / error / caption text ── */
    .stAlert, .stCaption, .stInfo {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #B9D4F1;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: Calibri, Trebuchet MS, Arial, sans-serif !important;
        color: #64748B;
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        color: #002147 !important;
        border-bottom: 2px solid #002147 !important;
    }

    /* ── Scrollbar styling ── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #EEF4FB;
    }
    ::-webkit-scrollbar-thumb {
        background: #75AADB;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #002147;
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
SEC_FILE = "data/SEC_Financials.csv"

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
st.title("TrendCast Dashboard")
st.markdown(
    '<div class="subtitle">Electronics market trend monitoring across Google Trends, news sources, Amazon reviews, and SEC financial data.</div>',
    unsafe_allow_html=True,
)

# ---------------- LOAD DATA FOR METRICS ----------------
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

try:
    sec_df = load_csv(SEC_FILE)
    sec_companies = sec_df["ticker"].nunique() if "ticker" in sec_df.columns else 0
except Exception:
    sec_companies = 0

# ---------------- KPI CARDS ----------------
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Google Keywords", google_keywords)
m2.metric("NewsAPI Keywords", newsapi_keywords)
m3.metric("NYT Keywords", nyt_keywords)
m4.metric("Amazon Categories", amazon_categories)
m5.metric("SEC Companies", sec_companies)

st.markdown("---")

# =========================================================
# GOOGLE TRENDS
# =========================================================
st.header("Google Trends")

try:
    google_df = load_csv(GOOGLE_TRENDS_FILE)

    gf1, gf2 = st.columns(2)
    with gf1:
        google_search = st.text_input("Search Google Trends keyword", "", key="google_search")
    with gf2:
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
st.header("News Trends")

try:
    newsapi_df = load_csv(NEWSAPI_COUNTS_FILE)
    nyt_counts_df = load_csv(NYT_COUNTS_FILE)

    nf1, nf2 = st.columns(2)
    with nf1:
        news_search = st.text_input("Search NewsAPI keyword", "", key="news_search")
    with nf2:
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
st.subheader("Live Headlines")

try:
    news_docs, nyt_docs = load_mongo_headlines()

    hf1, hf2 = st.columns(2)
    with hf1:
        mongo_news_search = st.text_input("Search live news headlines", "", key="mongo_news_search")
    with hf2:
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
                    <div class="headline-meta">{source} {"&bull; " + str(date) if date else ""}</div>
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
                    <div class="headline-meta">New York Times {"&bull; " + str(date) if date else ""}</div>
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
st.header("Product Insights (Amazon Reviews)")

try:
    amazon_df = load_csv(AMAZON_FILE)

    af1, af2 = st.columns(2)
    with af1:
        amazon_search = st.text_input("Search Amazon category", "", key="amazon_search")
    with af2:
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

st.markdown("---")

# =========================================================
# SEC FINANCIALS
# =========================================================
st.header("Financial Insights (SEC Data)")

try:
    sec_df = load_csv(SEC_FILE)

    sf1, sf2 = st.columns(2)
    with sf1:
        sec_search = st.text_input("Search company or ticker", "", key="sec_search")
    with sf2:
        if "ticker" in sec_df.columns:
            ticker_options = sorted(sec_df["ticker"].dropna().astype(str).unique().tolist())
            default_tickers = ticker_options[:3] if len(ticker_options) >= 3 else ticker_options
            selected_tickers = st.multiselect(
                "Select companies",
                options=ticker_options,
                default=default_tickers,
                key="sec_tickers"
            )
        else:
            selected_tickers = []

    filtered_sec = sec_df.copy()

    if "ticker" in filtered_sec.columns:
        filtered_sec["ticker"] = filtered_sec["ticker"].astype(str)

    if "name" in filtered_sec.columns:
        filtered_sec["name"] = filtered_sec["name"].astype(str)

    if sec_search:
        search_mask = False
        if "ticker" in filtered_sec.columns:
            search_mask = filtered_sec["ticker"].str.contains(sec_search, case=False, na=False)
        if "name" in filtered_sec.columns:
            name_mask = filtered_sec["name"].str.contains(sec_search, case=False, na=False)
            search_mask = search_mask | name_mask if isinstance(search_mask, pd.Series) else name_mask
        if isinstance(search_mask, pd.Series):
            filtered_sec = filtered_sec[search_mask]

    if selected_tickers and "ticker" in filtered_sec.columns:
        filtered_sec = filtered_sec[filtered_sec["ticker"].isin(selected_tickers)]

    if "fiscal_year" in filtered_sec.columns:
        filtered_sec["fiscal_year"] = filtered_sec["fiscal_year"].astype(str)

    if "revenue" in filtered_sec.columns:
        filtered_sec["revenue"] = (
            filtered_sec["revenue"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
    )
    filtered_sec["revenue"] = pd.to_numeric(filtered_sec["revenue"], errors="coerce")
    filtered_sec["revenue_billions"] = filtered_sec["revenue"] / 1e9

    if "net_income" in filtered_sec.columns:
        filtered_sec["net_income"] = (
            filtered_sec["net_income"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
    )
    filtered_sec["net_income"] = pd.to_numeric(filtered_sec["net_income"], errors="coerce")
    filtered_sec["net_income_billions"] = filtered_sec["net_income"] / 1e9

    if "eps" in filtered_sec.columns:
        filtered_sec["eps"] = (
            filtered_sec["eps"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
    )
    filtered_sec["eps"] = pd.to_numeric(filtered_sec["eps"], errors="coerce")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Revenue Over Time")
        if {"fiscal_year", "ticker", "revenue_billions"}.issubset(filtered_sec.columns):
            revenue_chart = filtered_sec.pivot_table(
                index="fiscal_year",
                columns="ticker",
                values="revenue_billions",
                aggfunc="mean"
            ).sort_index()
            if not revenue_chart.empty:
                st.line_chart(revenue_chart)
                st.caption("Revenue shown in billions USD.")
            else:
                st.info("No SEC revenue rows match the current filters.")
        else:
            st.info("Expected SEC revenue columns were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Net Income Over Time")
        if {"fiscal_year", "ticker", "net_income_billions"}.issubset(filtered_sec.columns):
            income_chart = filtered_sec.pivot_table(
                index="fiscal_year",
                columns="ticker",
                values="net_income_billions",
                aggfunc="mean"
            ).sort_index()
            if not income_chart.empty:
                st.line_chart(income_chart)
                st.caption("Net income shown in billions USD.")
            else:
                st.info("No SEC income rows match the current filters.")
        else:
            st.info("Expected SEC net income columns were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("EPS Comparison")
        if {"ticker", "eps"}.issubset(filtered_sec.columns):
            eps_chart = (
                filtered_sec.groupby("ticker", as_index=False)["eps"]
                .mean()
                .sort_values("eps", ascending=False)
            )
            if not eps_chart.empty:
                st.bar_chart(eps_chart.set_index("ticker"))
            else:
                st.info("No EPS rows match the current filters.")
        else:
            st.info("Expected SEC EPS columns were not found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Financial Data Table")
        st.dataframe(filtered_sec, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"SEC financial data error: {e}")