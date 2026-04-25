import json
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from src.models.anomaly_detector import AnomalyDetector

# -----------------------------
# Kafka Consumer (RAW)
# -----------------------------
consumer = KafkaConsumer(
    'supply-chain',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    group_id='ml-consumer-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# -----------------------------
# Kafka Producer (PROCESSED)
# -----------------------------
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚀 ML Consumer started...")

# -----------------------------
# Load + Train Model
# -----------------------------
detector = AnomalyDetector()
historical_df = pd.read_csv("data/supply_chain_data.csv")
detector.train(historical_df)

print("✅ Model trained")

# -----------------------------
# Stream Processing
# -----------------------------
for message in consumer:
    data = message.value

    input_data = {
        "demand": data["demand"],
        "inventory": data["inventory"],
        "lead_time": data.get("lead_time", 0)
    }

    anomaly = detector.predict(input_data)

    # Add ML result
    data["anomaly"] = anomaly

    # Better labeling
    if anomaly == 1:
        if data["inventory"] < 80:
            data["anomaly_type"] = "inventory_shortage"
        elif data["demand"] > 250:
            data["anomaly_type"] = "demand_spike"
        else:
            data["anomaly_type"] = "unknown"
    else:
        data["anomaly_type"] = "normal"

    print("📤 Sending processed:", data)

    # 🔥 Send to new topic
    producer.send("supply-chain-processed", value=data)