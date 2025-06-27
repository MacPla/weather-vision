
from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def index():
    try:
        with open("/shared/latest.txt") as f:
            status = f.read().strip()
    except:
        status = "Unknown"

    return f"""<h1>Weather Status</h1>
              <p><strong>Current:</strong> {status}</p>
              <meta http-equiv='refresh' content='10'>"""

app.run(host="0.0.0.0", port=8080)
