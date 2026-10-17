# Model artifacts

| Model | Scaler | Input features | Task |
|---|---|---:|---|
| `xgboost_model_v3.pkl` | `xgboost_scaler_v3.pkl` | 12 | Fault classification |
| `xgboost_multiclass_rul_prediction_ttf_240min_enhanced_tuned.json` | `scaler_multiclass_ttf_240min_enhanced_focused_tuned.pkl` | 160 | Time-to-failure / remaining-useful-life classification |

The RUL model and scaler are a matched pair. The model metadata reports 160 input features, and the scaler contains 160 fitted features.
