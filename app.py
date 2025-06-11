import base64

from flask import Flask, render_template, jsonify
import cv2

app = Flask(__name__)
latest_frame = None
latest_frame_2 = None
latest_pitch = None
latest_voronoi = None
console_lines = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    pitch_data = ""
    voronoi_data = ""
    frame_data = ""
    frame_data_2 = ""

    if latest_pitch is not None:
        _, buffer = cv2.imencode(".jpg", latest_pitch)
        pitch_data = buffer.tobytes()
        pitch_data = base64.b64encode(pitch_data).decode("utf-8")

    if latest_voronoi is not None:
        _, voronoi_buffer = cv2.imencode(".jpg", latest_voronoi)
        voronoi_data = voronoi_buffer.tobytes()
        voronoi_data = base64.b64encode(voronoi_data).decode("utf-8")

    if latest_frame is not None:
        _, frame_buffer = cv2.imencode(".jpg", latest_frame)
        frame_data = frame_buffer.tobytes()
        frame_data = base64.b64encode(frame_data).decode("utf-8")

    if latest_frame_2 is not None:
        _, frame_buffer_2 = cv2.imencode(".jpg", latest_frame_2)
        frame_data_2 = frame_buffer_2.tobytes()
        frame_data_2 = base64.b64encode(frame_data_2).decode("utf-8")

    return jsonify({
        "frame": frame_data,
        "frame2": frame_data_2,
        "pitch": pitch_data,
        "voronoi": voronoi_data,
        "warnings": console_lines[-100:]
    })

def update_dashboard(frame, frame_2, pitch, voronoi, warnings):
    global latest_pitch, console_lines, latest_voronoi, latest_frame, latest_frame_2

    if frame is not None:
        latest_frame = frame.copy()
    if pitch is not None:
        latest_pitch = pitch.copy()
    if voronoi is not None:
        latest_voronoi = voronoi.copy()
    if frame_2 is not None:
        latest_frame_2 = frame_2.copy()

    console_lines = warnings.copy()

def start_dashboard():
    app.run(debug=False, port=5050)