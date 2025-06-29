from flask import Flask, request, jsonify
import datetime
import json
import parsedatetime
from pytz import timezone
from calendar_service import format_slots, find_free_slots, book_meeting
from db import insert_user, get_user_by_phone

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
    firstName = data.get("firstName", "")
    lastName = data.get("lastName", "")

    if not any([phone, firstName, lastName]):
        return jsonify({"success": 0, "message": "Phone number and name are required"})

    with open("users.json", "r") as f:
        users = json.load(f)

    if phone in users:
        return jsonify({"success": 0, "message": "User already exists"})

    users[phone] = {
        "firstName": firstName,
        "lastName": lastName,
        "appointments": []
    }
    
    with open("users.json", "w") as f:
        json.dump(users, f)

    return jsonify({"success": 1, "message": "User added successfully"})

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
    phone = data.get("phone", "")
    start_time = data["start_time"]  # Format: 'YYYY-MM-DD HH:MM'
    end_time = data["end_time"]      # Format: 'YYYY-MM-DD HH:MM'
    title = data.get("title", "Appointment")
    description = data.get("description", "")

    # Schedule the appointment
    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
    event_link = book_meeting(start_dt, end_dt, title, description)

    # Save the appointment to the user's record
    with open("users.json", "r") as f:
        users = json.load(f)
    
    if phone not in users:
        return jsonify({"result": "User not found"}), 404
    
    users[phone]["appointments"].append({
        "start_time": start_dt.strftime('%Y-%m-%d %H:%M'),
        "end_time": end_dt.strftime('%Y-%m-%d %H:%M'),
        "title": title,
        "description": description,
        "event_link": event_link
    })

    with open("users.json", "w") as f:
        json.dump(users, f)
    
    return jsonify({"result": "Appointment booked successfully", "link": event_link})

# if __name__ == "__main__":
#     app.run(debug=True)
