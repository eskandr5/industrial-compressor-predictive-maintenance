import paho.mqtt.client as mqtt
import json
import time
import random
import os

# إعدادات MQTT
broker_address = os.getenv('MQTT_BROKER_HOST', '127.0.0.1')
port = int(os.getenv('MQTT_BROKER_PORT', '1883'))
topic = os.getenv('MQTT_TOPIC', 'compressor/data')

# إنشاء عميل MQTT
client = mqtt.Client(client_id=os.getenv('MQTT_CLIENT_ID', 'Synthetic_Telemetry_Publisher'))
client.connect(broker_address, port, 60)

# متغير لتتبع الوقت
start_time = time.time() / 60  # الوقت الأولي بالدقائق

# محاكاة بيانات الضاغط مع جميع الميزات المطلوبة
def generate_compressor_data(current_time):
    return {
        "time_min": current_time,  # الوقت بالدقائق
        "motor_rpm": round(random.uniform(1000, 3000), 2),
        "pressure_bar": round(random.uniform(1.0, 10.0), 2),
        "temperature_c": round(random.uniform(20.0, 80.0), 2),
        "vibration_rms": round(random.uniform(0.5, 5.0), 2),
        "power_kw": round(random.uniform(1.0, 10.0), 2),
        "airflow_demand_cfm": round(random.uniform(100, 500), 2),
        "torque_nm": round(random.uniform(50, 200), 2),
        "noise_db": round(random.uniform(60, 90), 2),
        "oilpump_power_w": round(random.uniform(100, 500), 2),
        "motor_health": round(random.uniform(0.7, 1.0), 2),
        "compressor_health": round(random.uniform(0.7, 1.0), 2),
        "tank_health": round(random.uniform(0.7, 1.0), 2),
        "blockage_factor": round(random.uniform(0, 1), 2),
        "leak_rate_lpm": round(random.uniform(0, 10), 2),
        "load_unload_cycles": round(random.uniform(0, 100), 2),
        "repair_status": random.randint(0, 1),
        "pressure_change_rate": round(random.uniform(-1, 1), 2),
        "temperature_change_rate": round(random.uniform(-1, 1), 2),
        "vibration_moving_avg": round(random.uniform(0.5, 5.0), 2),
        "time_since_last_repair": round(random.uniform(0, 1000), 2)
    }

# إرسال البيانات كل ثانية
try:
    counter = 0
    while True:
        current_time = start_time + (counter / 60)  # زيادة 1 ثانية = 1/60 دقيقة
        data = generate_compressor_data(current_time)
        message = json.dumps(data)
        client.publish(topic, message)
        print(f"Published: {message}")
        time.sleep(1)
        counter += 1
except KeyboardInterrupt:
    print("Stopped by user")
    client.disconnect()