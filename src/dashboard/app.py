import json
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import threading
from queue import Queue
from src.llm.insights_generator import generate_insights
from src.models.anomaly_detector import AnomalyDetector

# Try to import Kafka, but fallback to mock data if not available
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except:
    KAFKA_AVAILABLE = False

# -----------------------------
# GLOBAL STATE
# -----------------------------
data_queue = Queue(maxsize=500)
data_buffer = []
MAX_BUFFER = 500
anomaly_detector = AnomalyDetector()
model_trained = False
last_mock_date = datetime.now() - timedelta(hours=1)


# -----------------------------
# Mock Data Generator
# -----------------------------
def mock_data_generator():
    """Generate realistic mock supply chain data"""
    global last_mock_date
    
    print("🎲 Starting mock data generator...")
    
    while True:
        try:
            last_mock_date += timedelta(seconds=2)
            
            # Generate realistic patterns
            base_demand = 150
            demand_noise = random.gauss(0, 20)
            demand_spike = 50 if random.random() < 0.1 else 0  # 10% spike chance
            demand = max(50, base_demand + demand_noise + demand_spike)
            
            base_inventory = 100
            inventory_noise = random.gauss(0, 15)
            inventory = max(10, base_inventory + inventory_noise)
            
            lead_time = random.randint(1, 10)
            
            # Generate anomaly label
            anomaly = 1 if abs(demand_noise + demand_spike) > 40 else 0
            anomaly_type = "demand_spike" if demand_spike > 0 else "inventory_shortage" if inventory < 30 else "normal"
            
            data = {
                "date": last_mock_date.isoformat(),
                "demand": round(demand),
                "inventory": round(inventory),
                "lead_time": lead_time,
                "anomaly": anomaly,
                "anomaly_type": anomaly_type
            }
            
            if not data_queue.full():
                data_queue.put(data)
                print(f"📥 Generated: {data['date'][:19]} - Demand: {data['demand']}, Inventory: {data['inventory']}")
            
            time.sleep(2)  # Generate data every 2 seconds
            
        except Exception as e:
            print(f"⚠️  Mock data error: {e}")
            time.sleep(5)


# -----------------------------
# Kafka Consumer Thread (with fallback)
# -----------------------------
def kafka_listener():
    """Listen to Kafka or fall back to mock data"""
    if not KAFKA_AVAILABLE:
        print("⚠️  Kafka not available - using mock data instead")
        mock_data_generator()
        return
        
    try:
        consumer = KafkaConsumer(
            'supply-chain',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            group_id='dashboard-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            request_timeout_ms=3000
        )

        print("✅ Kafka connected. Listening...")

        for message in consumer:
            print("📥 Received:", message.value)
            if not data_queue.full():
                data_queue.put(message.value)

    except Exception as e:
        print(f"❌ Kafka Error: {e}")
        print("⚠️  Switching to mock data...")
        mock_data_generator()


threading.Thread(target=kafka_listener, daemon=True).start()


# -----------------------------
# Dash App
# -----------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("📦 Supply Chain Anomaly Detection Dashboard", 
                style={"marginBottom": "10px", "color": "#333"}),
        html.P("Real-time monitoring of supply chain metrics with AI-powered anomaly detection",
              style={"color": "#666", "marginBottom": "20px"})
    ], style={"backgroundColor": "#f8f9fa", "padding": "20px", "borderRadius": "10px", "marginBottom": "20px"}),

    # 🚨 ALERT BANNER
    html.Div(
        id="alert-banner",
        style={
            "backgroundColor": "#ff4d4d",
            "color": "white",
            "padding": "15px",
            "fontWeight": "bold",
            "display": "none",
            "borderRadius": "5px"
        }
    ),

    # KPI Cards
    html.Div(
        id="kpi-cards",
        style={
            "display": "flex", 
            "gap": "20px", 
            "marginBottom": "30px",
            "justifyContent": "space-around",
            "flexWrap": "wrap"
        }
    ),

    # Charts Section
    html.Div([
        html.H2("📈 Key Metrics", style={"marginBottom": "20px"}),
        html.Div([
            html.Div([
                dcc.Graph(id="demand-chart")
            ], style={"width": "48%", "display": "inline-block", "marginRight": "2%"}),
            html.Div([
                dcc.Graph(id="inventory-chart")
            ], style={"width": "48%", "display": "inline-block"})
        ], style={"display": "flex"})
    ], style={"marginBottom": "30px"}),

    # Anomalies Section
    html.Div([
        html.H2("🚨 Recent Anomalies", style={"marginBottom": "15px", "color": "#333"}),
        html.Div(id="anomaly-list", 
                style={
                    "border": "1px solid #ddd", 
                    "borderRadius": "5px", 
                    "padding": "15px",
                    "minHeight": "100px",
                    "backgroundColor": "#fafafa"
                })
    ], style={"marginBottom": "30px"}),

    # AI Insights
    html.Div([
        html.H2("🧠 AI Insights", style={"marginBottom": "15px", "color": "#333"}),
        html.Div(
            id="insights-box",
            style={
                "border": "2px solid #007BFF",
                "padding": "20px",
                "borderRadius": "10px",
                "backgroundColor": "#eef6ff",
                "minHeight": "150px",
                "fontFamily": "monospace",
                "fontSize": "14px"
            }
        )
    ], style={"marginBottom": "30px"}),

    # Refresh interval
    dcc.Interval(id="interval", interval=2000, n_intervals=0)
], style={"padding": "20px", "fontFamily": "Arial, sans-serif", "maxWidth": "1400px", "margin": "0 auto"})


# -----------------------------
# CALLBACK
# -----------------------------
@app.callback(
    [
        Output("demand-chart", "figure"),
        Output("inventory-chart", "figure"),
        Output("anomaly-list", "children"),
        Output("kpi-cards", "children"),
        Output("insights-box", "children"),
        Output("alert-banner", "children"),
        Output("alert-banner", "style")
    ],
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    global model_trained

    print("🔥 CALLBACK TRIGGERED")

    # Move queue → buffer
    while not data_queue.empty():
        data_buffer.append(data_queue.get())

    if len(data_buffer) > MAX_BUFFER:
        data_buffer.pop(0)

    print("📊 Buffer size:", len(data_buffer))

    if len(data_buffer) == 0:
        empty_fig = go.Figure().add_annotation(text="⏳ Waiting for streaming data... Is Kafka running?", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig, html.Div("No data yet"), [], html.Div("No insights yet"), "", {"display": "none"}

    df = pd.DataFrame(data_buffer)

    # Safe conversion
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["demand"] = pd.to_numeric(df["demand"], errors="coerce")
    df["inventory"] = pd.to_numeric(df["inventory"], errors="coerce")
    df["lead_time"] = pd.to_numeric(df["lead_time"], errors="coerce")

    df = df.dropna(subset=["date", "demand", "inventory"])

    if df.empty:
        empty_fig = go.Figure().add_annotation(text="❌ No valid data received", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return empty_fig, empty_fig, html.Div("No valid data"), [], html.Div("No insights"), "", {"display": "none"}

    # Train model if we have enough data
    if not model_trained and len(df) >= 10:
        try:
            anomaly_detector.train(df)
            model_trained = True
            print("✅ Anomaly detector trained")
        except Exception as e:
            print(f"⚠️  Model training error: {e}")

    # Predict anomalies
    if model_trained:
        try:
            df["anomaly"] = df.apply(
                lambda row: anomaly_detector.predict({
                    "demand": row["demand"],
                    "inventory": row["inventory"],
                    "lead_time": row["lead_time"]
                }),
                axis=1
            )
        except Exception as e:
            print(f"⚠️  Anomaly prediction error: {e}")
            df["anomaly"] = 0
    else:
        df["anomaly"] = df.get("anomaly", 0)  # Use provided anomaly or default to 0

    # Ensure anomaly_type exists
    if "anomaly_type" not in df.columns:
        df["anomaly_type"] = df["anomaly"].apply(lambda x: "detected" if x == 1 else "normal")

    # Sort by date
    df = df.sort_values("date")

    # Get anomalies
    anomalies = df[df["anomaly"] == 1]

    # -----------------------------
    # Charts with anomaly markers
    # -----------------------------
    demand_fig = px.line(df, x="date", y="demand", title="📈 Demand Trend", markers=True)
    
    if not anomalies.empty:
        demand_fig.add_scatter(
            x=anomalies["date"],
            y=anomalies["demand"],
            mode="markers",
            marker=dict(size=12, color="red", symbol="star"),
            name="Anomalies",
            hovertemplate="<b>Anomaly</b><br>Date: %{x}<br>Demand: %{y}<extra></extra>"
        )

    demand_fig.update_layout(hovermode="x unified", height=400)

    inventory_fig = px.line(df, x="date", y="inventory", title="📉 Inventory Trend", markers=True)
    
    if not anomalies.empty:
        inventory_fig.add_scatter(
            x=anomalies["date"],
            y=anomalies["inventory"],
            mode="markers",
            marker=dict(size=12, color="red", symbol="star"),
            name="Anomalies",
            hovertemplate="<b>Anomaly</b><br>Date: %{x}<br>Inventory: %{y}<extra></extra>"
        )

    inventory_fig.update_layout(hovermode="x unified", height=400)

    # -----------------------------
    # Anomaly list
    # -----------------------------
    if not anomalies.empty:
        anomaly_list = [
            html.Div(
                f"⚠️ {pd.to_datetime(row['date']).strftime('%H:%M:%S')} - {row['anomaly_type']}: Demand={row['demand']:.0f}, Inventory={row['inventory']:.0f}",
                style={"color": "red", "padding": "5px", "borderLeft": "3px solid red"}
            )
            for _, row in anomalies.tail(5).iterrows()
        ]
    else:
        anomaly_list = [html.Div("✅ No anomalies detected", style={"color": "green"})]

    # -----------------------------
    # KPI cards
    # -----------------------------
    kpis = [
        html.Div([
            html.H4("📦 Avg Demand"),
            html.P(f"{df['demand'].mean():.0f}", style={"fontSize": "24px", "color": "#007BFF"})
        ], style={"padding": "15px", "border": "1px solid #ccc", "borderRadius": "5px", "flex": "1"}),

        html.Div([
            html.H4("📊 Avg Inventory"),
            html.P(f"{df['inventory'].mean():.0f}", style={"fontSize": "24px", "color": "#28a745"})
        ], style={"padding": "15px", "border": "1px solid #ccc", "borderRadius": "5px", "flex": "1"}),

        html.Div([
            html.H4("🚨 Anomalies"),
            html.P(f"{len(anomalies)}", style={"fontSize": "24px", "color": "red" if len(anomalies) > 0 else "#666"})
        ], style={"padding": "15px", "border": "1px solid #ccc", "borderRadius": "5px", "flex": "1"})
    ]

    # -----------------------------
    # ALERT BANNER
    # -----------------------------
    if len(anomalies) > 0:
        alert_text = f"🚨 {len(anomalies)} anomalies detected!"
        alert_style = {
            "backgroundColor": "#ff4d4d",
            "color": "white",
            "padding": "15px",
            "fontWeight": "bold",
            "display": "block",
            "borderRadius": "5px",
            "marginBottom": "20px"
        }
    else:
        alert_text = ""
        alert_style = {"display": "none"}

    # -----------------------------
    # LLM Insights
    # -----------------------------
    try:
        insights = generate_insights(df.tail(50))
        insights_display = html.Div(insights, style={"whiteSpace": "pre-wrap", "lineHeight": "1.6"})
    except Exception as e:
        print(f"⚠️  Insights generation error: {e}")
        # Fallback insights based on data
        anomaly_pct = (len(anomalies) / len(df) * 100) if len(df) > 0 else 0
        demand_avg = df['demand'].mean()
        inventory_avg = df['inventory'].mean()
        insights_display = html.Div([
            html.P(f"📊 Current Statistics:"),
            html.Ul([
                html.Li(f"Average Demand: {demand_avg:.0f} units"),
                html.Li(f"Average Inventory: {inventory_avg:.0f} units"),
                html.Li(f"Anomaly Rate: {anomaly_pct:.1f}%"),
                html.Li(f"Data Points: {len(df)}")
            ]),
            html.P("💡 Tip: Install Ollama for AI-powered insights", style={"fontSize": "12px", "color": "#666"})
        ], style={"lineHeight": "1.6"})

    return demand_fig, inventory_fig, anomaly_list, kpis, insights_display, alert_text, alert_style


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)