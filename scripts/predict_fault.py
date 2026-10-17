import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(os.getenv('MODEL_DIR', str(PROJECT_ROOT / 'models')))
INPUT_FILE = Path(os.getenv('FAULT_INPUT_FILE', str(PROJECT_ROOT / 'data' / 'input.json')))

try:
    model = joblib.load(MODEL_DIR / 'xgboost_model_v3.pkl')
    scaler = joblib.load(MODEL_DIR / 'xgboost_scaler_v3.pkl')

    with INPUT_FILE.open('r', encoding='utf-8') as f:
        input_data = json.load(f)

    df = pd.DataFrame([input_data])

    features = [
        'vibration_rms', 'pressure_bar', 'temperature_c', 'power_kw',
        'pressure_change_rate', 'vibration_moving_avg', 'temperature_change_rate',
        'power_moving_avg', 'time_since_last_repair', 'torque_nm',
        'noise_db', 'oilpump_power_w'
    ]

    for feature in features:
        if feature not in df.columns:
            df[feature] = 0.0

    df[features] = df[features].apply(pd.to_numeric, errors='coerce').fillna(0.0)

    X = scaler.transform(df[features])
    X = np.array(X)

    expected_shape = (1, len(features))
    if X.shape != expected_shape:
        raise ValueError(f"Unexpected shape of X after scaling: {X.shape}, expected {expected_shape}")

    pred = model.predict(X)
    if not isinstance(pred, (list, np.ndarray)):
        raise ValueError(f"Prediction is not a list or numpy array: {type(pred)}")
    if len(pred) == 0:
        raise ValueError("Prediction returned an empty result")
    if len(pred) != 1:
        raise ValueError(f"Unexpected prediction length: {len(pred)}, expected 1")

    pred = pred[0]

    reverse_mapping = {0: -5, 1: -4, 2: -3, 3: -2, 4: -1, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4, 10: 5}
    fault_type = reverse_mapping[int(pred)]

    result = {'fault_type': int(fault_type)}
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({'error': str(e)}))