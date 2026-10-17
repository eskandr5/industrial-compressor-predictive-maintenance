import pandas as pd
import paho.mqtt.client as mqtt
import json
import time
import os
from pathlib import Path

# إعدادات MQTT
PROJECT_ROOT = Path(__file__).resolve().parents[1]
broker_address = os.getenv('MQTT_BROKER_HOST', '127.0.0.1')
broker_port = int(os.getenv('MQTT_BROKER_PORT', '1883'))
topic = os.getenv('MQTT_TOPIC', 'compressor/data')
client = mqtt.Client(client_id=os.getenv('MQTT_CLIENT_ID', 'CSV_Replay_Publisher'))

# الاتصال بخادم MQTT
try:
    client.connect(broker_address, broker_port, 60)
    print("Connected to MQTT broker")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)

# قراءة ملف البيانات
try:
    csv_file = Path(os.getenv('CSV_FILE', str(PROJECT_ROOT / 'data' / 'ttf.csv')))
    df = pd.read_csv(csv_file)
    print("CSV file loaded successfully")
except Exception as e:
    print(f"Failed to load CSV file: {e}")
    exit(1)

# الميزات المطلوبة (لتتطابق مع predict_fault4.py)
required_features = [
    'vibration_rms', 'pressure_bar', 'temperature_c', 'power_kw',
    'pressure_change_rate', 'vibration_moving_avg', 'temperature_change_rate',
    'power_moving_avg', 'time_since_last_repair', 'torque_nm',
    'noise_db', 'oilpump_power_w'
]

# نشر كل صف كرسالة MQTT
try:
    for index, row in df.iterrows():
        # إنشاء قاموس بالميزات المطلوبة فقط
        data = {feature: float(row.get(feature, 0)) for feature in required_features}
        # تحويل القاموس إلى سلسلة JSON
        message = json.dumps(data)
        # نشر الرسالة
        client.publish(topic, message)
        print(f"Published: {message}")
        time.sleep(1)  # تأخير بين الرسائل
except Exception as e:
    print(f"Failed to publish data: {e}")
finally:
    client.disconnect()
    print("Disconnected from MQTT broker")