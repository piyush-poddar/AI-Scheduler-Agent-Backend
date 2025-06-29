import psycopg
from dotenv import load_dotenv
import os

load_dotenv()
POSTGRES_URI = os.getenv("POSTGRES_URI", None)
if not POSTGRES_URI:
    raise ValueError("POSTGRES_URI environment variable is not set.")

def insert_user(
    phone: str,
    first_name: str,
    last_name: str
) -> int:
    """
    Insert a new user into the database.
    """
    try:
        # Insert a new user and return the user ID
        with psycopg.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (phone, first_name, last_name) VALUES (%s, %s, %s)",
                    (phone, first_name, last_name)
                )
                conn.commit()
                
                # Get the ID of the newly inserted user
                cur.execute("SELECT id FROM users WHERE phone = %s", (phone,))
                user_id = cur.fetchone()[0]
                return user_id
            
    except Exception as e:
        print(f"Error inserting user: {e}")
        return None

def get_user_by_phone(phone: str):
    """
    Get user details by phone number.
    """
    try:
        with psycopg.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                user = cur.fetchone()
                if user:
                    return {
                        "id": user[0],
                        "phone": user[1],
                        "first_name": user[2],
                        "last_name": user[3]
                    }
                else:
                    return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def insert_appointment(
    user_id: int,
    date: str,
    start_time: str,
    event_id: str,
    description: str,
):
    """
    Insert a new appointment for a user.
    """
    try:
        with psycopg.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO appointments (user_id, date, start_time, description, event_id) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, date, start_time, description, event_id)
                )
                conn.commit()
    except Exception as e:
        print(f"Error inserting appointment: {e}")

# user = get_user_by_phone("9560779666")
# print(user)