import base64

from flask import Flask, render_template, jsonify
import cv2

app = Flask(__name__)
latest_frame = None
console_lines = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    frame_data = ""
    if latest_frame is not None:
        _, buffer = cv2.imencode(".jpg", latest_frame)
        frame_data = buffer.tobytes()
        frame_data = base64.b64encode(frame_data).decode("utf-8")

    return jsonify({
        "frame": frame_data,
        "warnings": console_lines[-100:]  # Last 100 lines
    })

def update_dashboard(frame, warnings):
    global latest_frame, console_lines
    if frame is not None:
        latest_frame = frame.copy()
    console_lines = warnings.copy()

def start_dashboard():
    app.run(debug=False, port=5000)