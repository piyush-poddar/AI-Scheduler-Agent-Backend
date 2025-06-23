from flask import Flask, request, jsonify
import datetime
from calendar_service import format_slots, find_free_slots, book_meeting

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Google Calendar Free Slots API is running"})

@app.route("/get_free_slots", methods=["GET"])
def get_free_slots():
    date = request.args.get("date")  # Format: 'YYYY-MM-DD'
    duration_minutes = int(request.args.get("duration_minutes", 60))
    slots = format_slots(find_free_slots(date, duration_minutes))
    return jsonify({"free_slots": slots})

@app.route("/book_meeting", methods=["POST"])
def book_meeting_endpoint():
    data = request.get_json()
    start_time = data["start_time"]  # Format: 'YYYY-MM-DD HH:MM'
    end_time = data["end_time"]      # Format: 'YYYY-MM-DD HH:MM'
    title = data.get("title", "Meeting")

    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
    event_link = book_meeting(start_dt, end_dt, title)
    return jsonify({"result": "Meeting booked successfully", "link": event_link})