import os

from influxdb_client import InfluxDBClient, Point
from dotenv import load_dotenv

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")


class InfluxWriter:

    def __init__(self):

        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )

        self.write_api = self.client.write_api()

    def write_vital_signs(self, data):

        point = (
            Point("vital_signs")
            .tag("ward_id", data["ward_id"])
            .tag("bed_id", data["bed_id"])
            .field("heart_rate", int(data["heart_rate"]))
            .field("spo2", float(data["spo2"]))
            .field("body_temp", float(data["body_temp"]))
            .field("respiration_rate", int(data["respiration_rate"]))
            .field("systolic_bp", int(data["systolic_bp"]))
            .field("diastolic_bp", int(data["diastolic_bp"]))
        )

        self.write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

    def write_event(self, event):

        point = (
            Point("ward_events")
            .tag("bed_id", event["bed_id"])
            .tag("event_type", event["event_type"])
            .tag("severity", event["severity"])
            .field("value", float(event["value"]))
            .field("threshold", str(event["threshold"]))
        )

        self.write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

    def write_actuator_status(self, status):

        point = (
            Point("actuator_status")
            .tag("bed_id", status["bed_id"])
            .field("nurse_call", bool(status["nurse_call"]))
            .field("light", bool(status["light"]))
            .field("oxygen", bool(status["oxygen"]))
        )

        self.write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

    def close(self):

        self.client.close()
