import os
import json

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from rule_engine import RuleEngine
from influx_writer import InfluxWriter

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

TOPIC_SENSOR = "ward/+/sensor/telemetry"

bed_states = {}

engine = RuleEngine()

try:
    influx = InfluxWriter()
except Exception as e:
    print("InfluxDB disabled:", e)
    influx = None


def validate(data):

    required = [
        "ward_id",
        "bed_id",
        "heart_rate",
        "spo2",
        "body_temp",
        "respiration_rate",
        "systolic_bp",
        "diastolic_bp",
        "bed_occupancy",
        "fall_detected",
        "timestamp"
    ]

    for field in required:
        if field not in data:
            print("Missing field:", field)
            return False

    if not str(data["bed_id"]).strip():
        return False

    try:
        int(data["heart_rate"])
        float(data["spo2"])
        float(data["body_temp"])
        int(data["respiration_rate"])
        int(data["systolic_bp"])
        int(data["diastolic_bp"])
        int(data["timestamp"])
    except Exception:
        return False

    return True


def normalize(data):

    return {
        "ward_id": str(data["ward_id"]),
        "bed_id": str(data["bed_id"]),
        "heart_rate": int(data["heart_rate"]),
        "spo2": float(data["spo2"]),
        "body_temp": float(data["body_temp"]),
        "respiration_rate": int(data["respiration_rate"]),
        "systolic_bp": int(data["systolic_bp"]),
        "diastolic_bp": int(data["diastolic_bp"]),
        "bed_occupancy": bool(data["bed_occupancy"]),
        "fall_detected": bool(data["fall_detected"]),
        "timestamp": int(data["timestamp"])
    }


def publish_event(client, bed_id, event):

    topic = f"ward/{bed_id}/gateway/event"

    client.publish(
        topic,
        json.dumps(event)
    )


def publish_command(client, bed_id, command):

    topic = f"ward/{bed_id}/actuator/command"

    payload = {
        "target": command["target"],
        "action": command["action"],
        "reason": command["reason"]
    }

    client.publish(
        topic,
        json.dumps(payload)
    )


def on_connect(client, userdata, flags, rc):

    print("Connected:", rc)

    client.subscribe(TOPIC_SENSOR)

    print("Subscribed:", TOPIC_SENSOR)


def on_message(client, userdata, msg):

    try:

        raw_data = json.loads(msg.payload.decode())

        if not validate(raw_data):
            print("Invalid telemetry")
            return

        data = normalize(raw_data)

        bed_id = data["bed_id"]

        bed_states[bed_id] = data

        print("\n===== TELEMETRY =====")
        print(f"Bed: {bed_id}")
        print(
            f"HR={data['heart_rate']} "
            f"SpO2={data['spo2']} "
            f"T={data['body_temp']}"
        )

        if influx:
            influx.write_vital_signs(data)

        events, commands = engine.evaluate(data)

        for event in events:

            print("EVENT:", event)

            publish_event(
                client,
                bed_id,
                event
            )

            if influx:
                influx.write_event(event)

        for command in commands:

            print("COMMAND:", command)

            publish_command(
                client,
                bed_id,
                command
            )

    except Exception as e:
        print("Error:", e)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    MQTT_HOST,
    MQTT_PORT,
    60
)

print("Gateway started...")

client.loop_forever()

