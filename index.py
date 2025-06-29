from flask import Flask, request, jsonify
import datetime
import json
import parsedatetime
from pytz import timezone
from calendar_service import format_slots, find_free_slots, book_meeting
from db import insert_user, get_user_by_phone, insert_appointment, get_appointment, update_appointment

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def root():
    return jsonify({"message": "Scheduler Agent API is running"})

@app.route("/api/user/get", methods=["GET"])
def check_user():
    """
    Get user details by phone number if it exists.
    """
    phone = request.args.get("phone", "")
    if not phone:
        return jsonify({"exists": 0, "message": "Phone number is required"})
    
    user = get_user_by_phone(phone)
    if user:
        return jsonify({"exists": 1, "data": user})
    
    return jsonify({"exists": 0, "data": {}})

@app.route("/api/user/add", methods=["POST"])
def add_user():
    """
    Add a new user with phone number and name.
    """
    data = request.get_json()
    phone = data.get("phone", "")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")

    if not any([phone, first_name, last_name]):
        return jsonify({"success": 0, "message": "Phone number and name are required"})

    user_id = insert_user(phone, first_name, last_name)

    return jsonify({"success": 1, "user_id": user_id, "message": "User added successfully"})

@app.route("/api/parse-datetime", methods=["GET"])
def parse_datetime():
    """
    Parse a natural language date/time string into a datetime object.
    Use this tool to interpret user input like "today", "next Tuesday" or "in 2 hours".

    Args:
        text (str): Natural language date/time string.

    Returns:
        datetime.datetime: Parsed datetime object, or None if parsing fails.
    """
    text = request.args.get("text", "")

    IST = timezone('Asia/Kolkata')
    now_ist = datetime.datetime.now(IST)

    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(text, now_ist.timetuple())

    if parse_status == 0:
        return None

    dt_ist = datetime.datetime(*time_struct[:6])

    return jsonify({
        "date": dt_ist.strftime('%Y-%m-%d'),
    })

@app.route("/api/get-free-slots", methods=["GET"])
def get_free_slots():
    date = request.args.get("date")  # Format: 'YYYY-MM-DD'
    duration_minutes = int(request.args.get("duration_minutes", 60))
    slots = format_slots(find_free_slots(date, duration_minutes))
    
    return jsonify({"free_slots": slots})

@app.route("/api/book-meeting", methods=["POST"])
def book_meeting_endpoint():
    data = request.get_json()
    user_id = data.get("user_id", "")
    start_time = data["start_time"]  # Format: 'YYYY-MM-DD HH:MM'    
    title = data.get("title", "Appointment")
    description = data.get("description", "Consultation Appointment")

    # Schedule the appointment
    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    # Add 60 minutes to the start time for the end time
    end_dt = start_dt + datetime.timedelta(minutes=60)
    event_link, event_id = book_meeting(start_dt, end_dt, title, description)
    
    if not event_link:
        return jsonify({"error": "Failed to book the meeting"}), 500
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Insert the appointment into the database
    insert_appointment(user_id, start_dt.strftime('%Y-%m-%d'), start_dt.strftime('%H:%M'), event_id, description)
    
    return jsonify({"success": 1, "result": "Appointment booked successfully", "event_id": event_id})

@app.route("/api/appointment/get", methods=["GET"])
def get_appointment_details(
    user_id: int,
    date: str,
    start_time: str
):
    """
    Get appointment details for a user on a specific date and time.
    """
    appointment = get_appointment(user_id, date, start_time)
    
    if not appointment:
        return jsonify({"success": 0, "message": "No appointment found"}), 404
    
    return jsonify({"success": 1, "data": appointment})

@app.route("/api/appointment/update", methods=["PUT"])
def update_appointment_endpoint():
    """
    Update an existing appointment for a user using appointment_id.
    """
    data = request.get_json()
    appointment_id = data.get("appointment_id")
    date = data.get("date")
    start_time = data.get("start_time")
    description = data.get("description", "")
    event_id = data.get("event_id", "")

    if not any([appointment_id, date, start_time, description, event_id]):
        return jsonify({"success": 0, "message": "Appointment ID, date, and start time are required"}), 400

    update_appointment(appointment_id, date, start_time, description, event_id)
    
    return jsonify({"success": 1, "message": "Appointment updated successfully"})

# if __name__ == "__main__":
#     app.run(debug=True)
