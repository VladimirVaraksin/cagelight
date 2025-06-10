import base64

from flask import Flask, render_template, jsonify
import cv2

app = Flask(__name__)
latest_frame = None
latest_voronoi = None
console_lines = []
done = False

@app.route("/status")
def status():
    return jsonify({"done": done})


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    frame_data = ""
    voronoi_data = ""
    if latest_frame is not None:
        _, buffer = cv2.imencode(".jpg", latest_frame)
        frame_data = buffer.tobytes()
        frame_data = base64.b64encode(frame_data).decode("utf-8")

    if latest_voronoi is not None:
        _, voronoi_buffer = cv2.imencode(".jpg", latest_voronoi)
        voronoi_data = voronoi_buffer.tobytes()
        voronoi_data = base64.b64encode(voronoi_data).decode("utf-8")

    return jsonify({
        "frame": frame_data,
        "voronoi": voronoi_data,
        "warnings": console_lines[-100:]
    })

def update_dashboard(frame, voronoi, warnings, done_status=False):
    if done_status:
        global done
        done = True
        return
    global latest_frame, console_lines, latest_voronoi
    if frame is not None:
        latest_frame = frame.copy()
    if voronoi is not None:
        latest_voronoi = voronoi.copy()
    console_lines = warnings.copy()

def start_dashboard():
    app.run(debug=False, port=5050)