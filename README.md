# 📦 Supply Chain Anomaly Detection & Streaming Dashboard

A real-time, AI-powered supply chain analytics platform that detects anomalies, forecasts demand, and generates actionable insights from streaming data using machine learning and LLMs.

## 🎯 Key Features

✅ **Real-Time Anomaly Detection** - Isolates unusual patterns in demand, inventory, and lead times using Isolation Forest ML model

✅ **Live Data Streaming** - Kafka-based architecture for scalable, real-time data ingestion

✅ **Interactive Dashboard** - Plotly-based UI with real-time charts, KPI cards, and anomaly alerts

✅ **AI-Powered Insights** - Ollama integration for natural language analysis and recommendations

✅ **Demand Forecasting** - Prophet-based time-series forecasting with seasonal decomposition

✅ **Mock Data Support** - Built-in mock data generator for testing without Kafka

✅ **Docker Ready** - Pre-configured docker-compose for instant Kafka deployment

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.8+ |
| **Data Processing** | Pandas, NumPy |
| **ML/Anomaly Detection** | Scikit-learn (Isolation Forest) |
| **Forecasting** | Prophet |
| **Real-time Streaming** | Apache Kafka |
| **Dashboard** | Plotly Dash |
| **LLM Integration** | Ollama (Local) |
| **Containerization** | Docker & Docker Compose |

---

## 📋 Prerequisites

- **Python 3.8+**
- **Docker & Docker Desktop** (for Kafka; optional - app has mock data fallback)
- **Git**

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd supply-chain-anomaly-detection-dashboard
pip install -r requirements.txt
```

### 2️⃣ Start Kafka (Optional - App Works Without It!)

```bash
docker-compose up -d
```

### 3️⃣ Start the Dashboard

```bash
python -m src.dashboard.app
```

You should see:
```
🎲 Starting mock data generator...
Dash is running on http://127.0.0.1:8050
```

### 4️⃣ Open in Browser

Navigate to: **http://localhost:8050**

---

## 📊 Dashboard Components

### KPI Cards
- **Average Demand**: Real-time demand metrics
- **Average Inventory**: Current inventory levels
- **Anomaly Count**: Number of detected anomalies

### Trend Charts
- **Demand Trend**: Historical demand with anomaly markers (red stars ⭐)
- **Inventory Trend**: Inventory levels with anomaly indicators

### Anomaly Detection
- **Recent Anomalies**: Last 5 detected anomalies with timestamps
- **Anomaly Types**: demand_spike, inventory_shortage, etc.

### AI Insights
- **Statistical Analysis**: Volatility, coverage, trends
- **Recommendations**: Best practices for supply chain management
- **AI-Enhanced** (Optional): Connect Ollama for advanced insights

### Alert Banner
- **Red Alert**: Triggered when anomalies are detected
- **Real-time**: Updates every 2 seconds

---

## 🏗️ Project Structure

```
supply-chain-anomaly-detection-dashboard/
│
├── src/
│   ├── dashboard/
│   │   └── app.py              # Main Dash application
│   │
│   ├── data_pipeline/
│   │   ├── producer.py         # Kafka data producer
│   │   └── consumer.py         # Kafka data consumer
│   │
│   ├── models/
│   │   ├── anomaly_detector.py # ML anomaly detection
│   │   └── forecast.py         # Prophet forecasting
│   │
│   ├── llm/
│   │   └── insights_generator.py # Ollama integration
│   │
│   └── utils/
│       ├── config.py           # Configuration settings
│       └── __init__.py
│
├── data/
│   └── supply_chain_data.csv   # Sample dataset
│
├── notebooks/
│   └── (Jupyter notebooks for exploration)
│
├── docker-compose.yml          # Kafka + Zookeeper setup
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── RUNNING.md                  # Detailed setup guide
├── FIXES_SUMMARY.md            # Recent improvements
└── .gitignore                  # Privacy-focused ignore rules
```

---

## 🚀 How It Works

### Data Flow

```
Producer (Generates Data) 
    ↓
Kafka Topic: supply-chain
    ↓
Dashboard Consumer (Listens)
    ↓
Data Buffer (stores last 500 points)
    ↓
ML Processing:
  ├─ Isolation Forest (Anomaly Detection)
  ├─ Statistical Analysis
  └─ LLM Insights
    ↓
Plotly Visualization
    ↓
Real-time Dashboard Updates
```

### Anomaly Detection Logic

- **Model**: Isolation Forest (Scikit-learn)
- **Trigger**: Training starts at 10+ data points
- **Features**: demand, inventory, lead_time
- **Contamination Rate**: 5% (0.05)
- **Update Frequency**: Every 2 seconds

---

## 🧠 AI Insights (Optional)

### With Ollama (Advanced)

1. **Install Ollama**: https://ollama.ai
2. **Pull Model**:
   ```bash
   ollama pull llama2
   ```
3. **Start Service**:
   ```bash
   ollama serve
   ```
4. **Restart Dashboard**:
   ```bash
   python -m src.dashboard.app
   ```

The dashboard automatically detects Ollama and provides AI-generated insights!

### Without Ollama (Fallback)

The app provides statistical insights:
- Demand volatility analysis
- Inventory coverage calculation
- Anomaly rate metrics
- Safety stock recommendations

---

## 🔧 Configuration

Edit `src/utils/config.py` to customize:

```python
# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'supply-chain'

# Model settings
ANOMALY_CONTAMINATION = 0.05  # 5% contamination rate
MODEL_TRAINING_THRESHOLD = 10  # Train after 10 points

# Dashboard settings
DATA_BUFFER_SIZE = 500
UPDATE_INTERVAL = 2000  # milliseconds
```

---

## 📈 Sample Data Format

```json
{
  "date": "2026-04-25T16:30:45.123456",
  "demand": 165,
  "inventory": 95,
  "lead_time": 5,
  "anomaly": 0,
  "anomaly_type": "normal"
}
```

---

## 🐛 Troubleshooting

### Graphs Not Updating?

**Check 1**: Is the data generator running?
```bash
# You should see messages like:
# 📥 Generated: 2026-04-25T... - Demand: 145, Inventory: 98
```

**Check 2**: Clear browser cache
- Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

**Check 3**: Check browser console for errors
- Press `F12` → Console tab

### Kafka Connection Issues?

The dashboard automatically falls back to mock data. You'll see:
```
⚠️  Kafka not available - using mock data instead
```

This is normal! The mock data generator provides realistic test data.

### Ollama Not Connecting?

The app has a built-in fallback with statistical insights. To enable AI:
1. Install Ollama: https://ollama.ai
2. Verify it's running: `http://localhost:11434`
3. Restart dashboard

### Port Already in Use (Port 8050)?

```bash
# Find process using port 8050
netstat -ano | findstr :8050

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

---

## 📊 Example Use Cases

| Scenario | Detection |
|----------|-----------|
| **Sudden Demand Spike** | Marked as anomaly, alert triggered |
| **Inventory Shortage** | Red star on chart, flagged in insights |
| **Lead Time Delay** | Integrated into anomaly score |
| **Normal Operations** | Green status, no alerts |

---

## 🔐 Privacy & Security

- **Sensitive data excluded**: `.gitignore` protects credentials
- **No hardcoded secrets**: Use `.env` file for configuration
- **Local LLM**: Ollama runs locally (no cloud data transfer)
- **Docker isolation**: Kafka runs in containers

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | Latest | Data manipulation |
| numpy | Latest | Numerical computing |
| scikit-learn | Latest | ML models |
| prophet | Latest | Time-series forecasting |
| plotly | Latest | Interactive charts |
| dash | Latest | Dashboard framework |
| kafka-python | Latest | Streaming data |
| requests | Latest | HTTP client for Ollama |
| python-dotenv | Latest | Environment variables |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

- **Documentation**: See [RUNNING.md](RUNNING.md) for detailed setup
- **Issues**: Check [FIXES_SUMMARY.md](FIXES_SUMMARY.md) for common fixes
- **Questions**: Open an issue on GitHub

---

## 🎓 Learning Resources

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Plotly Dash Guide](https://dash.plotly.com/)
- [Scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Prophet Forecasting](https://facebook.github.io/prophet/)
- [Ollama Models](https://ollama.ai)

---

**Built with ❤️ for supply chain analytics**
