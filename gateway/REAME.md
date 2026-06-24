# Ward Gateway

Edge IoT Gateway for the Virtual Smart Healthcare Ward Gateway project.

## Features

* Subscribe telemetry from virtual sensors via MQTT
* Validate telemetry messages
* Normalize incoming data into a standard format
* Maintain latest state for each bed
* Execute rule engine for emergency detection
* Generate events and actuator commands
* Store telemetry and events into InfluxDB

## Project Structure

```
gateway/
├── main.py
├── rule_engine.py
├── influx_writer.py
├── requirements.txt
├── Dockerfile
└── .env
```

## MQTT Topics

Subscribe:

```
ward/+/sensor/telemetry
```

Publish:

```
ward/{bed_id}/gateway/event
ward/{bed_id}/actuator/command
```

## Rule Engine

* HR > 120 or HR < 50 → hr_abnormal
* SpO2 < 92 → spo2_low
* Temperature > 38.5°C → fever
* fall_detected = true → fall_detected

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Author

SV2 - Edge Gateway, Rule Engine, InfluxDB
