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
            return False

    return True


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

        data = json.loads(msg.payload.decode())

        if not validate(data):
            print("Invalid telemetry")
            return

        bed_id = data["bed_id"]

        bed_states[bed_id] = data

        print("\n===== TELEMETRY =====")
        print(bed_id)
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

client.loop_forever()

