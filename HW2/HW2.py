import luigi
import pandas as pd
import mysql.connector
import requests
from datetime import datetime, timedelta
import os


DB_CONFIG = {
    "host": "localhost",
    "user": "student",
    "password": "1234",
    "database": "autobusu_parkas"
}

WORK_DIR = "/tmp/bus_workflow"
os.makedirs(WORK_DIR, exist_ok=True)


class ExtractInternalData(luigi.Task):
    def output(self):
        return luigi.LocalTarget(f"{WORK_DIR}/internal_data_done.txt")

    def run(self):
        conn = mysql.connector.connect(**DB_CONFIG)

        routes = pd.read_sql("SELECT * FROM routes", conn)
        timetables = pd.read_sql("SELECT * FROM timetables", conn)
        stops = pd.read_sql("SELECT * FROM stops", conn)
        stopping_points = pd.read_sql("SELECT * FROM stopping_points", conn)

        routes.to_csv(f"{WORK_DIR}/routes.csv", index=False)
        timetables.to_csv(f"{WORK_DIR}/timetables.csv", index=False)
        stops.to_csv(f"{WORK_DIR}/stops.csv", index=False)
        stopping_points.to_csv(f"{WORK_DIR}/stopping_points.csv", index=False)

        conn.close()

        with self.output().open("w") as f:
            f.write("Internal data extracted successfully\n")


class FetchExternalData(luigi.Task):
    def output(self):
        return luigi.LocalTarget(f"{WORK_DIR}/external_data_done.txt")

    def run(self):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 54.6872,
            "longitude": 25.2797,
            "hourly": "temperature_2m,precipitation"
        }

        response = requests.get(url, params=params, timeout=20)
        weather = response.json()

        weather_df = pd.DataFrame([{
            "temperature": weather["hourly"]["temperature_2m"][0],
            "precipitation": weather["hourly"]["precipitation"][0]
        }])

        weather_df.to_csv(f"{WORK_DIR}/weather.csv", index=False)

        with self.output().open("w") as f:
            f.write("External data fetched successfully\n")


class TransformAndPredict(luigi.Task):
    def requires(self):
        return [ExtractInternalData(), FetchExternalData()]

    def output(self):
        return luigi.LocalTarget(f"{WORK_DIR}/predicted_arrivals.csv")

    def run(self):
        weather = pd.read_csv(f"{WORK_DIR}/weather.csv")

        departure = datetime(2026, 3, 31, 7, 50)

        segments = [
            ("Vilnius", "Elektrėnai", 40, 0.8, "Heavy traffic"),
            ("Elektrėnai", "Kryžkalnis", 80, 0.9, "Road works"),
            ("Kryžkalnis", "Klaipėda", 115, 1.0, None)
        ]

        precipitation_penalty = 0
        if float(weather.loc[0, "precipitation"]) > 0:
            precipitation_penalty = 3

        time_calc = departure
        results = [{
            "stop": "Vilnius",
            "planned": "07:50",
            "predicted": "07:50",
            "delay": 0,
            "reason": "Start"
        }]

        planned_times = {
            "Elektrėnai": departure + timedelta(minutes=40),
            "Kryžkalnis": departure + timedelta(minutes=120),
            "Klaipėda": departure + timedelta(minutes=235)
        }

        for seg in segments:
            duration = round(seg[2] / seg[3]) + precipitation_penalty
            time_calc += timedelta(minutes=duration)

            delay = int((time_calc - planned_times[seg[1]]).total_seconds() / 60)

            reasons = []
            if seg[4]:
                reasons.append(seg[4])
            if precipitation_penalty > 0:
                reasons.append("Weather impact")

            results.append({
                "stop": seg[1],
                "planned": planned_times[seg[1]].strftime("%H:%M"),
                "predicted": time_calc.strftime("%H:%M"),
                "delay": delay,
                "reason": ", ".join(reasons) if reasons else "On time"
            })

        result_df = pd.DataFrame(results)
        result_df.to_csv(self.output().path, index=False)


class SaveResultsToDatabase(luigi.Task):
    def requires(self):
        return TransformAndPredict()

    def output(self):
        return luigi.LocalTarget(f"{WORK_DIR}/save_done.txt")

    def run(self):
        result_df = pd.read_csv(f"{WORK_DIR}/predicted_arrivals.csv")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predicted_arrivals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stop_name VARCHAR(100),
                planned_time VARCHAR(10),
                predicted_time VARCHAR(10),
                delay_minutes INT,
                reason TEXT
            )
        """)
        conn.commit()

        cursor.execute("DELETE FROM predicted_arrivals")
        conn.commit()

        for _, row in result_df.iterrows():
            cursor.execute("""
                INSERT INTO predicted_arrivals
                (stop_name, planned_time, predicted_time, delay_minutes, reason)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                row["stop"],
                row["planned"],
                row["predicted"],
                int(row["delay"]),
                row["reason"]
            ))

        conn.commit()
        cursor.close()
        conn.close()

        with self.output().open("w") as f:
            f.write("Results saved to database successfully\n")


if __name__ == "__main__":
    luigi.run()
