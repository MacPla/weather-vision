from flask import Flask, render_template, send_from_directory
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route("/")
def index():
    try:
        with open("/shared/latest.txt") as f:
            status = f.read().strip()
        with open("/shared/timestamp.txt") as f:
            timestamp = f.read().strip()
    except:
        status = "Unknown"
        timestamp = "N/A"

    img_url = "/shared/last.jpg"

    history = []
    now = datetime.now()
    for i in range(12):
        hour = now - timedelta(hours=i)
        base = hour.strftime("%Y-%m-%d_%H")
        img_path = f"/shared/history/{base}.jpg"
        txt_path = f"/shared/history/{base}.txt"
        if os.path.exists(img_path) and os.path.exists(txt_path):
            with open(txt_path) as tf:
                status_hour = tf.read().strip()
            history.append({
                "time": hour.strftime("%H:%M"),
                "status": status_hour,
                "image_url": f"/shared/history/{base}.jpg"
            })

    return render_template("index.html", status=status, timestamp=timestamp, img_url=img_url, history=history)

@app.route('/shared/<path:filename>')
def shared_files(filename):
    return send_from_directory('/shared', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
