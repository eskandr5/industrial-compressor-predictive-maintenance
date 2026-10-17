import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = Path(os.getenv('MODEL_DIR', str(PROJECT_ROOT / 'models')))
TTF_MODEL_FILE = Path(os.getenv('TTF_MODEL_FILE', str(MODEL_DIR / 'xgboost_multiclass_rul_prediction_ttf_240min_enhanced_tuned.json')))
TTF_SCALER_FILE = Path(os.getenv('TTF_SCALER_FILE', str(MODEL_DIR / 'scaler_multiclass_ttf_240min_enhanced_focused_tuned.pkl')))
HISTORY_FILE = Path(os.getenv('TTF_HISTORY_FILE', str(PROJECT_ROOT / 'data' / 'data_history.csv')))

# دالة لإنشاء الميزات المشتقة
def create_features(data_df):
    data_df = data_df.sort_values(by='time_min').reset_index(drop=True)
    data_df = data_df.copy()
    epsilon = 1e-8

    window_sizes_minutes = [5, 10, 30, 60, 120]
    window_sizes_points = [size * 60 for size in window_sizes_minutes]
    core_features = ['pressure_bar', 'temperature_c', 'vibration_rms', 'power_kw']

    for window_size in window_sizes_points:
        if window_size > len(data_df):
            continue  # تجاهل النافذة دون طباعة تحذير

        for col in core_features:
            data_df[f'{col}_mean_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=1).mean()
            data_df[f'{col}_std_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=1).std()
            data_df[f'{col}_min_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=1).min()
            data_df[f'{col}_max_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=1).max()
            if window_size > 2:
                data_df[f'{col}_skew_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=3).skew()
                data_df[f'{col}_kurt_{window_size//60}min'] = data_df[col].rolling(window=window_size, min_periods=3).kurt()

        for col in core_features:
            data_df[f'{col}_diff_{window_size//60}min'] = data_df[col].diff(periods=window_size)
            data_df[f'time_diff_{window_size//60}min'] = data_df['time_min'].diff(periods=window_size)
            data_df[f'{col}_change_rate_{window_size//60}min'] = data_df[f'{col}_diff_{window_size//60}min'] / (data_df[f'time_diff_{window_size//60}min'] + epsilon)
            data_df = data_df.drop(columns=[f'{col}_diff_{window_size//60}min', f'time_diff_{window_size//60}min'], errors='ignore')

    data_df = data_df.fillna(method='bfill').fillna(0)
    return data_df

try:
    # تحميل النموذج والـ Scaler
    model = xgb.XGBClassifier()
    model.load_model(str(TTF_MODEL_FILE))
    scaler = joblib.load(TTF_SCALER_FILE)

    # قراءة التاريخ من ملف
    history_file = HISTORY_FILE
    if not history_file.exists():
        raise FileNotFoundError("History file not found. Please ensure data is being logged.")

    history_df = pd.read_csv(history_file)

    # التحقق من وجود العمود 'time_min'
    if 'time_min' not in history_df.columns:
        raise KeyError("Column 'time_min' not found in data_history.csv")

    # التحقق من أن جميع القيم في 'time_min' يمكن تحويلها إلى أرقام
    history_df['time_min'] = pd.to_numeric(history_df['time_min'], errors='coerce')
    if history_df['time_min'].isna().any():
        raise ValueError("Some values in 'time_min' column are not numeric")

    # التحقق من وجود بيانات كافية (120 دقيقة = 7200 نقطة)
    min_required_points = 7200
    if len(history_df) < min_required_points:
        raise ValueError(f"Not enough data points. Found {len(history_df)}, required {min_required_points} (120 minutes).")

    # الحفاظ على آخر 7200 نقطة
    history_df = history_df.tail(min_required_points)

    # حفظ التاريخ المحدث
    history_df.to_csv(history_file, index=False)

    # إذا لم يكن هناك بيانات، أعد تشغيل الكود لاحقًا
    if history_df.empty:
        raise ValueError("History file is empty. Waiting for new data.")

    # حساب الميزات المشتقة
    df = create_features(history_df)

    # تحديد الميزات المستخدمة
    core_features = ['pressure_bar', 'temperature_c', 'vibration_rms', 'power_kw']
    window_sizes_minutes = [5, 10, 30, 60, 120]
    derived_features = []
    for window in window_sizes_minutes:
        for col in core_features:
            derived_features.extend([
                f'{col}_mean_{window}min',
                f'{col}_std_{window}min',
                f'{col}_min_{window}min',
                f'{col}_max_{window}min',
                f'{col}_change_rate_{window}min'
            ])
            if window > 2:
                derived_features.extend([
                    f'{col}_skew_{window}min',
                    f'{col}_kurt_{window}min'
                ])

    original_features = [
        'motor_rpm', 'pressure_bar', 'temperature_c', 'vibration_rms', 'power_kw',
        'airflow_demand_cfm', 'torque_nm', 'noise_db', 'oilpump_power_w',
        'motor_health', 'compressor_health', 'tank_health', 'blockage_factor',
        'leak_rate_lpm', 'load_unload_cycles', 'repair_status', 'pressure_change_rate',
        'temperature_change_rate', 'vibration_moving_avg', 'time_since_last_repair'
    ]
    features = original_features + derived_features

    # التحقق من وجود جميع الميزات
    for feature in features:
        if feature not in df.columns:
            raise ValueError(f"Feature {feature} not found in the data")

    # تحويل جميع القيم إلى أرقام
    df[features] = df[features].apply(pd.to_numeric, errors='coerce')
    if df[features].isna().any().any():
        raise ValueError("Some feature values could not be converted to numeric")

    # أخذ آخر صف فقط للتنبؤ (البيانات الأحدث)
    X = scaler.transform(df[features].tail(1))
    X = np.array(X)

    # التحقق من شكل البيانات
    expected_shape = (1, len(features))
    if X.shape != expected_shape:
        raise ValueError(f"Unexpected shape of X after scaling: {X.shape}, expected {expected_shape}")

    # التنبؤ
    pred = model.predict(X)
    if not isinstance(pred, (list, np.ndarray)):
        raise ValueError(f"Prediction is not a list or numpy array: {type(pred)}")
    if len(pred) == 0:
        raise ValueError("Prediction returned an empty result")
    if len(pred) != 1:
        raise ValueError(f"Unexpected prediction length: {len(pred)}, expected 1")

    pred = pred[0]

    # إرجاع النتيجة
    result = {'ttf_class': int(pred)}
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({'error': str(e)}))