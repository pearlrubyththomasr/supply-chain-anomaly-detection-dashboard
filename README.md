# 📦 Supply Chain Anomaly Detection & Streaming Dashboard

## 🚀 Overview

A real-time supply chain analytics system that detects anomalies in demand, inventory, and logistics using time-series machine learning and streaming pipelines.

The system integrates forecasting, anomaly detection, and AI-generated insights into an interactive dashboard.

---

## ⚙️ Tech Stack

* Python, Pandas
* Prophet (Forecasting)
* Isolation Forest (Anomaly Detection)
* Kafka (Real-time streaming)
* Plotly Dash (Dashboard)
* Ollama (Local LLM for insights)

---

## 📊 Features

* Real-time anomaly detection on streaming data
* Demand forecasting using Prophet
* Kafka-based data ingestion pipeline
* Interactive dashboard with KPI tracking
* AI-generated supply chain health reports

---

## 🧠 Architecture

1. Data Generation → Kafka Producer
2. Kafka Consumer → Data Processing
3. ML Models → Detect anomalies + forecast
4. Dashboard → Visualize insights
5. LLM → Generate plain-English reports

---

## 🏗️ Project Structure

(see folder layout)

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python app.py
```
