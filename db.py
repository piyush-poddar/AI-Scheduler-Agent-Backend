import psycopg

def insert_user(
    phone: str,
    first_name: str,
    last_name: str
):
    """
    Insert a new user into the database.
    """
    try:
        with psycopg.connect("postgresql://postgres.pokxwxbxkagjejmpxtxr:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (phone, first_name, last_name) VALUES (%s, %s, %s)",
                    (phone, first_name, last_name)
                )
                conn.commit()
    except Exception as e:
        print(f"Error inserting user: {e}")

def get_user_by_phone(phone: str):
    """
    Get user details by phone number.
    """
    try:
        with psycopg.connect("postgresql://postgres.pokxwxbxkagjejmpxtxr:redhat@aws-0-ap-south-1.pooler.supabase.com:5432/postgres") as conn:
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
    
user = get_user_by_phone("9560779666")
print(user)