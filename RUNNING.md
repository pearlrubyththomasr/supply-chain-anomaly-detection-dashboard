# Running the Supply Chain Anomaly Detection Dashboard

## Prerequisites
- Python 3.8+
- Docker & Docker Compose (for Kafka)
- Ollama (optional, for AI insights)

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Start Kafka
```bash
docker-compose up -d
```

Or manually with Kafka:
```bash
# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

## Step 3: Start Data Producer (Terminal 1)
```bash
python -m src.data_pipeline.producer
```

You should see: `Sent: {"date": "2025-04-25...", "demand": 150, ...}`

## Step 4: Start Dashboard (Terminal 2)
```bash
python -m src.dashboard.app
```

You should see: `Dash is running on http://127.0.0.1:8050`

## Step 5: Open Dashboard
Navigate to `http://localhost:8050` in your browser

## Troubleshooting

### Graphs not showing?
- ✅ Check: Is Kafka running? (`docker ps` should show Kafka container)
- ✅ Check: Is producer running and sending data? (Look for "Sent:" messages)
- ✅ Check: Browser console for JS errors (F12 → Console)
- ✅ Solution: The dashboard shows "Waiting for streaming data... Is Kafka running?" when no data arrives

### Insights not showing?
- The dashboard shows basic statistical insights by default
- For AI insights, install and run Ollama:
  ```bash
  # Install from https://ollama.ai
  ollama pull llama2
  ollama serve
  ```

### Port Already in Use?
```bash
# Find and kill process using port 8050
lsof -i :8050
kill -9 <PID>
```

## Expected Behavior

1. **Startup**: Dashboard loads with "Waiting for streaming data..." message
2. **Data Arrives**: Charts populate with demand and inventory trends
3. **Anomalies**: Red star markers appear on charts when anomalies detected
4. **Insights**: AI-generated insights appear in the insights box
5. **Alerts**: Red banner shows when anomalies are detected

## Dashboard Components

- **KPI Cards**: Average demand, inventory, and anomaly count
- **Demand Chart**: Real-time demand trend with anomaly markers
- **Inventory Chart**: Real-time inventory trend with anomaly markers
- **Recent Anomalies**: List of last 5 detected anomalies
- **AI Insights**: Analysis and recommendations
- **Alert Banner**: Highlights when anomalies are detected
