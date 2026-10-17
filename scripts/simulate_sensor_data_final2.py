import pandas as pd
import paho.mqtt.client as mqtt
import json
import time
import os
from pathlib import Path

# MQTT settings
PROJECT_ROOT = Path(__file__).resolve().parents[1]
broker_address = os.getenv('MQTT_BROKER_HOST', '127.0.0.1')
broker_port = int(os.getenv('MQTT_BROKER_PORT', '1883'))
topic = os.getenv('MQTT_TOPIC', 'compressor/data')
client = mqtt.Client(client_id=os.getenv('MQTT_CLIENT_ID', 'RaspberryPi_Publisher'))

# Connect to the MQTT broker
try:
    client.connect(broker_address, broker_port, 60)
    print("Connected to MQTT broker")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

# Read the CSV file
try:
    csv_file = Path(os.getenv('CSV_FILE', str(PROJECT_ROOT / 'data' / 'ttf.csv')))
    df = pd.read_csv(csv_file)
    print("CSV file loaded successfully")
except Exception as e:
    print(f"Failed to load CSV file: {e}")
    exit(1)

# الميزات المطلوبة فقط
required_features = [
    'vibration_rms', 'pressure_bar', 'temperature_c', 'power_kw',
    'pressure_change_rate', 'vibration_moving_avg', 'temperature_change_rate',
    'power_moving_avg', 'time_since_last_repair', 'torque_nm',
    'noise_db', 'oilpump_power_w'
]

# Publish each row as an MQTT message
try:
    for index, row in df.iterrows():
        # أخذ الميزات المطلوبة فقط
        data = {feature: row.get(feature, 0) for feature in required_features}
        message = json.dumps(data)
        client.publish(topic, message)
        print(f"Published: {message}")
        time.sleep(1)  # تأخير بين الرسائل
except Exception as e:
    print(f"Failed to publish data: {e}")
finally:
    client.disconnect()
    print("Disconnected from MQTT broker")