import psycopg2

DB_CONFIG = {
    "host": "dpg-d0pi8f6uk2gs739m9c40-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "cagelight",
    "user": "cagelight",
    "password": "lC8JmUvTst9rI5bfUyZWSQyClqrdVrNN"
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
        timestamp VARCHAR(15),
        confidence FLOAT,
        camera_id INTEGER,
        action VARCHAR(30),
        x_min FLOAT, 
        y_min FLOAT, 
        x_max FLOAT, 
        y_max FLOAT
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()

def insert_record(entry):
    object_type = entry.get("object_type", "").lower()

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
        object_type,
        entry.get("team"),
        pitch_x,
        pitch_y,
        entry.get("timestamp", "00:00:000"),
        entry.get("confidence", 0.0),
        entry.get("camera_id", 0),
        entry.get("action", ""),  # This can be "unknown", "", or actual label
        x_min,
        y_min,
        x_max,
        y_max
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()

def insert_many_players(entries):
    for objects in entries:
        for player in objects:
            insert_record(player)