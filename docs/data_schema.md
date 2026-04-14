# TrendCast Data Schema

## 1. Main Dashboard Table

**Table: trend_summary**

| Column | Type | Description |
|------|------|------------|
| keyword | TEXT | Search keyword |
| keyword_group | TEXT | categorical / company / feature |
| trend_score | FLOAT | Final combined score |
| sentiment_score | FLOAT | NLP sentiment (-1 to 1) |
| news_count | INT | Number of news articles |
| google_trends_score | FLOAT | Search popularity |
| updated_at | DATE | Last updated |

---

## 2. Time Series Table

**Table: trend_over_time**

| Column | Type | Description |
|------|------|------------|
| keyword | TEXT | Search keyword |
| date | DATE | Date |
| trend_score | FLOAT | Trend score over time |
| sentiment_score | FLOAT | Sentiment over time |
| news_count | INT | News count over time |
| google_trends_score | FLOAT | Search trends over time |

---

## 3. Financial Data Table

**Table: company_financials**

| Column | Type | Description |
|------|------|------------|
| company | TEXT | Company name |
| date | DATE | Reporting date |
| revenue | FLOAT | Company revenue |
| eps | FLOAT | Earnings per share |
| net_income | FLOAT | Net income |

---

## Notes

- Company names must match keywords exactly (e.g., Apple, NVIDIA)
- This ensures clean joins across datasets
