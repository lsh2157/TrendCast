# MongoDB Data Source

This module contains MongoDB connection and query logic for TrendCast.

## Collections
- `news_articles`
- `nytimes_articles`
- `amazon_reviews`

## Purpose
MongoDB stores unstructured and semi-structured data such as:
- news articles from NewsAPI
- articles from NYTimes
- Amazon electronics reviews

These collections support:
- keyword search
- product review analysis
- news retrieval
- NLP sentiment analysis
- trend scoring

This data is intended to feed downstream processing and dashboard outputs.
