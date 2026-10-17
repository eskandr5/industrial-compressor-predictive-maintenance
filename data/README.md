# Telemetry datasets

| File | Rows | Role |
|---|---:|---|
| `data.csv` | 100,000 | Telemetry replay dataset without `time_to_failure` labels |
| `ttf.csv` | 50,000 | Telemetry dataset with `time_to_failure` and `fault_type` labels; default input for the CSV publisher |
| `enhanced_compressor_data_v4_modified_power_noise.csv` | 100,000 | Exploratory compressor dataset used in the research notebook |

The CSV replay publisher sends sensor fields as JSON messages to MQTT topic `compressor/data`. Set `CSV_FILE` to select a different dataset. The replay datasets contain compressor measurements and derived operating features. `data.csv` has no `time_to_failure` column; `ttf.csv` includes it.

`input.json` and `data_history.csv` are runtime files used by Node-RED and the inference scripts.
