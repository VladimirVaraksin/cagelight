import psycopg2
from psycopg2 import sql


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
        object_type VARCHAR(20),
        team VARCHAR(20),
        object_position FLOAT[],
        timestamp FLOAT,
        confidence FLOAT,
        camera_id INTEGER,
        action VARCHAR(20),
        x_center FLOAT,
        y_center FLOAT,
        width FLOAT,
        height FLOAT
    );
    """
    with get_connection() as conn: # Establish a connection to the database
        with conn.cursor() as cur: # Create a cursor to execute the query
            cur.execute(query) # Execute the create table query
            conn.commit() # Commit the transaction to save changes


def insert_player_record(player): # Insert a single player record into the database
    query = """
    INSERT INTO realtime_player_positions (
        tracking_id, object_type, team, object_position,
        timestamp, confidence, camera_id, action,
        x_center, y_center, width, height
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); 
    """
    values = (
        player.get("tracking_id"),
        player.get("object_type"),
        player.get("team"),
        player.get("object_position", [0.0, 0.0, 0.0, 0.0]),
        player.get("timestamp", 0.0),
        player.get("confidence", 0.0),
        player.get("camera_id", 0),
        player.get("action", "unknown"),
        player.get("x_center", 0.0),
        player.get("y_center", 0.0),
        player.get("width", 0.0),
        player.get("height", 0.0)
    )
    with get_connection() as conn: # Establish a connection to the database
        with conn.cursor() as cur: # Create a cursor to execute the query
            cur.execute(query, values) # Execute the insert query with the provided values
            conn.commit() # Commit the transaction to save changes


def insert_many_players(players): # Insert multiple player records
    for player in players: # Iterate through each player record
        insert_player_record(player) # Insert each player record into the database