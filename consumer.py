from kafka import KafkaConsumer
import psycopg2
import json

try:
    consumer = KafkaConsumer(
        "flute_notes",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest',
        group_id='flute-group'
    )
except Exception as e:
    print("Failed to start Kafka consumer:", e)
    exit(1)

try:
    conn = psycopg2.connect("dbname=flute user=postgres password=postgres host=localhost")
    cur = conn.cursor()
except Exception as e:
    print("Failed to connect to Postgres:", e)
    exit(1)

print("Consumer started. Listening for note changes...")

prev_note = None

for msg in consumer:
    try:
        event = msg.value
        curr_note = event["note"]

        if curr_note != prev_note:
            cur.execute(
                "INSERT INTO notes (ts, pattern, note) VALUES (%s, %s, %s)",
                (event["timestamp"], event["pattern"], event["note"])
            )
            conn.commit()
            print("Saved to DB:", event)
            prev_note = curr_note
        else:
            print("Note unchanged, skipped:", curr_note)

    except Exception as e:
        print("Error processing message:", e)
