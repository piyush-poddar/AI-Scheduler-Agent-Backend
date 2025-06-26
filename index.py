from flask import Flask, request, jsonify
import datetime
import parsedatetime
from pytz import timezone
from calendar_service import format_slots, find_free_slots, book_meeting

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def root():
    return jsonify({"message": "Scheduler Agent API is running"})

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

    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(text)
    
    if parse_status == 0:
        return None
    
    dt_native = datetime.datetime(*time_struct[:6])

    server_tz = datetime.datetime.now().astimezone().tzinfo
    dt_server = server_tz.localize(dt_native) if hasattr(server_tz, 'localize') else dt_native.replace(tzinfo=server_tz)

    IST = timezone('Asia/Kolkata')
    dt_ist = dt_server.astimezone(IST).replace(tzinfo=None)
    
    return jsonify({
        "dt_native": dt_native.isoformat(),
        "server_tz": str(server_tz),
        "dt_server": dt_server.isoformat(),
        "dt_ist": dt_ist.isoformat()
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
    start_time = data["start_time"]  # Format: 'YYYY-MM-DD HH:MM'
    end_time = data["end_time"]      # Format: 'YYYY-MM-DD HH:MM'
    title = data.get("title", "Meeting")

    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
    end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
    event_link = book_meeting(start_dt, end_dt, title)
    return jsonify({"result": "Meeting booked successfully", "link": event_link})

# if __name__ == "__main__":
#     app.run(debug=True)
