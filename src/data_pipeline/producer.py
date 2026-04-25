import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚀 Producer started...")

while True:
    try:
        data = {
            "date": str(datetime.now()),
            "demand": random.randint(100, 300),
            "inventory": random.randint(50, 200),
            "lead_time": random.randint(1, 10),
            "anomaly": random.choice([0, 1]),
            "anomaly_type": random.choice(["None", "demand_spike", "inventory_shortage"])
        }

        producer.send("supply-chain", value=data)
        producer.flush()

        print("Sent:", data)

        time.sleep(2)  # simulate streaming

    except Exception as e:
        print("❌ Producer error:", e)
        time.sleep(5)