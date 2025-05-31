import psycopg2


DB_CONFIG = {
    "host": "dpg-d0pi8f6uk2gs739m9c40-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "cagelight",
    "user": "cagelight",
    "password": "lC8JmUvTst9rI5bfUyZWSQyClqrdVrNN"
}





def get_connection():
    return psycopg2.connect(**DB_CONFIG) # Create a connection to the PostgreSQL database using the provided configuration

# I seperate the bounding box values in order to follow the rule of normal forms in database design.
def create_player_table():
    query = """
    CREATE TABLE IF NOT EXISTS realtime_player_positions (
        id SERIAL PRIMARY KEY,
        tracking_id INTEGER,
        object_type VARCHAR(15),
        team VARCHAR(10),
        pitch_x FLOAT,
        pitch_y FLOAT,
        timestamp VARCHAR(10),
        confidence FLOAT,
        camera_id INTEGER,
        action VARCHAR(30),
        x_min FLOAT, 
        y_min FLOAT, 
        x_max FLOAT, 
        y_max FLOAT
    );
    """
    with get_connection() as conn: # Establish a connection to the database
        with conn.cursor() as cur: # Create a cursor to execute the query
            cur.execute(query) # Execute the query to create the table if it does not exist
            conn.commit() # Commit the changes to the database

def insert_record(entry):
    query = """
    INSERT INTO realtime_player_positions (
        tracking_id, object_type, team, pitch_x, pitch_y,
        timestamp, confidence, camera_id, action,
        x_min, y_min, x_max, y_max
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    pitch_x, pitch_y = entry.get("pitch_position", [0.0, 0.0]) # Default to 0.0 for pitch_x and pitch_y if not provided
    x_min, y_min, x_max, y_max = entry.get("bbox_xyxy", [0.0, 0.0, 0.0, 0.0]) # Default to 0.0 for all bbox values if not provided
    values = (
        entry.get("tracking_id"), # Use 0 for ball tracking_id
        entry.get("object_type"), # Use "ball" for ball object_type
        entry.get("team"),
        pitch_x,
        pitch_y,
        entry.get("timestamp", 0.0), # Default timestamp to 0.0 if not provided
        entry.get("confidence", 0.0), # Default confidence to 0.0 if not provided
        entry.get("camera_id", 0),
        entry.get("action", "unknown"), # Default action to "unknown"
        x_min,
        y_min,
        x_max,
        y_max
    )
    with get_connection() as conn: #
        with conn.cursor() as cur: # Create a cursor to execute the query
            cur.execute(query, values) # Execute the query with the provided values
            conn.commit()

def insert_many_players(entries):
    for objects in entries:
        for player in objects: # Iterate through each player in the objects list
            #print player for debugging
            #print(player)
            insert_record(player) # Insert each player record into the database
