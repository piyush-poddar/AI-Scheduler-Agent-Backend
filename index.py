from fastapi import FastAPI
from mangum import Mangum
import datetime
from calendar_service import format_slots, find_free_slots, book_meeting
from pydantic import BaseModel

app = FastAPI()
handler = Mangum(app)

@app.get("/")
def root():
    return {"message": "Google Calendar Free Slots API is running"}

@app.get("/get_free_slots")
async def get_free_slots(
    date: str,  # Format: 'YYYY-MM-DD'
    duration_minutes: int = 60
):
    slots = format_slots(find_free_slots(date, duration_minutes))
    return {"free_slots": slots}

class BookMeetingRequest(BaseModel):
    start_time: str  # Format: 'YYYY-MM-DD HH:MM'
    end_time: str    # Format: 'YYYY-MM-DD HH:MM'
    title: str = "Meeting"

@app.post("/book_meeting")
async def book_meeting_endpoint(
    request: BookMeetingRequest
):
    start_dt = datetime.datetime.strptime(request.start_time, '%Y-%m-%d %H:%M')
    end_dt = datetime.datetime.strptime(request.end_time, '%Y-%m-%d %H:%M')
    event_link = book_meeting(start_dt, end_dt, request.title)
    return {"result": "Meeting booked successfully"}
