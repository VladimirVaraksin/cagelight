# This script is used to create a PostgreSQL table for storing player positions and insert records into it.
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "Player_Position",
    "user": "postgres",
    "password": "Manasseh1"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_player_table():
    query = """
    CREATE TABLE IF NOT EXISTS realtime_player_positions (
        id SERIAL PRIMARY KEY,
        tracking_id INTEGER,
        object_type VARCHAR(15),
        team VARCHAR(10),
        pitch_x FLOAT,
        pitch_y FLOAT,
        timestamp FLOAT,
        confidence FLOAT,
        camera_id SERIAL,
        action VARCHAR(30),
        x_min FLOAT,
        y_min FLOAT,
        x_max FLOAT,
        y_max FLOAT

    );
    """
    with get_connection() as conn: # Establish a connection to the database
        with conn.cursor() as cur: # Create a cursor to execute the query
            cur.execute(query) # Execute the creation table query
            conn.commit() # Commit the transaction to save changes


def insert_record(entry): # Insert a single entry into the database
    query = """
        INSERT INTO realtime_player_positions (
            tracking_id, object_type, team, pitch_x, pitch_y,
            timestamp, confidence, camera_id, action,
            x_min, y_min, x_max, y_max
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    pitch_x, pitch_y = entry.get("pitch_position", [0.0, 0.0])
    x_min, y_min, x_max, y_max = entry.get("bbox_xyxy", [0.0, 0.0, 0.0, 0.0])
    values = (
        entry.get("tracking_id"),
        entry.get("object_type"),
        entry.get("team"),
        pitch_x,
        pitch_y,
        entry.get("timestamp", 0.0),
        entry.get("confidence", 0.0),
        entry.get("camera_id", 0),
        entry.get("action", "unknown"),
        x_min,
        y_min,
        x_max,
        y_max
    )
    with get_connection() as conn: # Establish a connection to the database
            with conn.cursor() as cur: # Create a cursor to execute the query
                cur.execute(query, values) # Execute the insert query with the provided values
                conn.commit() # Commit the transaction to save changes


def insert_many_players(entries): # Insert multiple entry records
    for obj in entries: # Iterate through each entry record
        insert_record(obj) # Insert each entry record into the database