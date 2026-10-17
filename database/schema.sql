CREATE DATABASE IF NOT EXISTS compressor_data;
USE compressor_data;

CREATE TABLE IF NOT EXISTS compressor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    time_min DOUBLE,
    motor_rpm DOUBLE,
    pressure_bar DOUBLE,
    temperature_c DOUBLE,
    vibration_rms DOUBLE,
    power_kw DOUBLE,
    airflow_demand_cfm DOUBLE,
    torque_nm DOUBLE,
    noise_db DOUBLE,
    oilpump_power_w DOUBLE,
    motor_health DOUBLE,
    compressor_health DOUBLE,
    tank_health DOUBLE,
    blockage_factor DOUBLE,
    leak_rate_lpm DOUBLE,
    load_unload_cycles DOUBLE,
    repair_status INT,
    pressure_change_rate DOUBLE,
    temperature_change_rate DOUBLE,
    vibration_moving_avg DOUBLE,
    time_since_last_repair DOUBLE,
    `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rul_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    RUL_value FLOAT,
    prediction_meta JSON
);
