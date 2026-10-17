import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import sys
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(os.getenv('MODEL_DIR', str(PROJECT_ROOT / 'models')))

try:
    # تحميل النموذج والـ Scaler
    model = joblib.load(MODEL_DIR / 'xgboost_model_v3.pkl')
    scaler = joblib.load(MODEL_DIR / 'xgboost_scaler_v3.pkl')

    # قراءة البيانات من الأوامر
    input_data = json.loads(sys.argv[1])
    df = pd.DataFrame([input_data])

    # تحديد الميزات المستخدمة
    features = [
        'vibration_rms', 'pressure_bar', 'temperature_c', 'power_kw',
        'pressure_change_rate', 'vibration_moving_avg', 'temperature_change_rate',
        'power_moving_avg', 'time_since_last_repair', 'torque_nm',
        'noise_db', 'oilpump_power_w'
    ]

    # التأكد من أن جميع الميزات موجودة
    for feature in features:
        if feature not in df.columns:
            df[feature] = 0

    # تحويل جميع القيم إلى أرقام
    df[features] = df[features].apply(pd.to_numeric, errors='coerce').fillna(0)

    # تحجيم البيانات
    X = scaler.transform(df[features])
    X = np.array(X)  # التأكد من أن X هي مصفوفة NumPy
    if X.shape != (1, 12):
        raise ValueError(f"Unexpected shape of X after scaling: {X.shape}, expected (1, 12)")

    # التنبؤ
    pred = model.predict(X)
    if len(pred) == 0:
        raise ValueError("Prediction returned an empty result")
    if len(pred) != 1:
        raise ValueError(f"Unexpected prediction length: {len(pred)}, expected 1")

    pred = pred[0]  # أخذ القيمة الأولى

    # تحويل التنبؤ إلى الفئة الأصلية
    reverse_mapping = {0: -5, 1: -4, 2: -3, 3: -2, 4: -1, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5}
    fault_type = reverse_mapping[int(pred)]

    # إرجاع النتيجة
    result = {'fault_type': int(fault_type)}
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({'error': str(e)}))