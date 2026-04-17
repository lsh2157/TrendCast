# 🚀 TrendCast Data Pipeline Support：

This repository contains the core data pipeline that powers our project. Follow these steps to set up the environment and start feeding data into your local databases.

---

## 🛠 1. Pre-requisites (Before you start)

Please ensure you have the following installed on your computer:
1. **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (Essential for running Kafka and Databases).
2. **Python 3.8 or higher**: [Download here](https://www.python.org/downloads/).
3. **A Code Editor**: (e.g., VS Code or PyCharm).

---

## 🏃 2. Quick Start Guide (The 3 Steps)

### Step 1: Start the Infrastructure (Docker)
Open your terminal (Command Prompt or Terminal app), navigate to this folder, and run this code :
```bash
docker-compose up -d

- What this does: It automatically sets up Kafka, MongoDB, and PostgreSQL in the background. You don't need to install these programs manually!

- Verification: Open Docker Desktop; you should see "mongodb", "some-postgres", and "kafka" containers running.


### Step 2: Install Python Libraries
In the same terminal, run this code:
pip install -r requirements.txt

- What this does: Installs all necessary Python tools (Kafka-python, PyMongo, Psycopg2) required to run the scripts.

### Step 3: Run the Data Consumer
Finally, run the script that moves data from Kafka to the Databases by running this code:
python consumer_to_bd.py

- Success Indicator: You should see messages like ✅ PostgreSQL connection succeeded and 📊 [SQL] saved trends: ... scrolling on your screen.


📊 3. How to check the data?
- For PostgreSQL (Member 5 / Member 2)
If you need to see the "Google Trends" data for your charts:

Open your database tool (or use terminal).

Connect to: localhost:5432, Database: trendcast, User: postgres.

Table name: google_trends.



- For MongoDB (News Articles)
Connection string: mongodb://localhost:27017/

Database: TrendCastDB | Collection: articles.