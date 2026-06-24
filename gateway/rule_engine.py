class RuleEngine:
    HR_HIGH = 120
    HR_LOW = 50
    SPO2_LOW = 92
    SPO2_CRITICAL = 88
    TEMP_HIGH = 38.5

    def evaluate(self, telemetry):
        events = []
        commands = []

        bed_id = telemetry["bed_id"]

        hr = telemetry["heart_rate"]
        spo2 = telemetry["spo2"]
        temp = telemetry["body_temp"]
        fall = telemetry["fall_detected"]

        # Rule 1: Heart Rate
        if hr > self.HR_HIGH or hr < self.HR_LOW:
            events.append({
                "bed_id": bed_id,
                "event_type": "hr_abnormal",
                "severity": "critical",
                "value": hr,
                "threshold": f"{self.HR_LOW}-{self.HR_HIGH}"
            })

            commands.append({
                "target": "nurse_call",
                "action": "on",
                "reason": "hr_abnormal"
            })

        # Rule 2: SpO2
        if spo2 < self.SPO2_LOW:

            severity = (
                "critical"
                if spo2 < self.SPO2_CRITICAL
                else "warning"
            )

            events.append({
                "bed_id": bed_id,
                "event_type": "spo2_low",
                "severity": severity,
                "value": spo2,
                "threshold": self.SPO2_LOW
            })

            commands.append({
                "target": "oxygen",
                "action": "on",
                "reason": "spo2_low"
            })

            commands.append({
                "target": "nurse_call",
                "action": "on",
                "reason": "spo2_low"
            })

        # Rule 3: Fever
        if temp > self.TEMP_HIGH:

            events.append({
                "bed_id": bed_id,
                "event_type": "fever",
                "severity": "warning",
                "value": temp,
                "threshold": self.TEMP_HIGH
            })

            commands.append({
                "target": "nurse_call",
                "action": "on",
                "reason": "fever"
            })

        # Rule 4: Fall Detection
        if fall:

            events.append({
                "bed_id": bed_id,
                "event_type": "fall_detected",
                "severity": "critical",
                "value": 1,
                "threshold": 1
            })

            commands.append({
                "target": "nurse_call",
                "action": "on",
                "reason": "fall_detected"
            })

        return events, commands
