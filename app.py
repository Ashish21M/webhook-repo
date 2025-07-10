from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import pytz

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["events"]

def format_event(data):
    event_type = data.get("action")
    author = data.get("author", "Unknown")
    to_branch = data.get("to_branch", "")
    from_branch = data.get("from_branch", "")
    timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).strftime("%d %B %Y - %I:%M %p UTC")

    if event_type == "push":
        return f"{author} pushed to {to_branch} on {timestamp}"
    elif event_type == "pull_request":
        return f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
    elif event_type == "merge":
        return f"{author} merged branch {from_branch} to {to_branch} on {timestamp}"
    else:
        return "Unknown event"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data:
        formatted = format_event(data)
        collection.insert_one({"message": formatted, "timestamp": datetime.utcnow()})
        return jsonify({"status": "success", "message": formatted}), 201
    return jsonify({"status": "error", "message": "Invalid payload"}), 400

@app.route("/events", methods=["GET"])
def get_events():
    events = collection.find().sort("timestamp", -1).limit(10)
    return jsonify([e["message"] for e in events])

if __name__ == "__main__":
    app.run(debug=True)
