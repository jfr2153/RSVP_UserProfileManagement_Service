import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Function to establish a database connection
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME'),
        port=int(os.environ.get('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# Pydantic models
class User(BaseModel):
    id: Optional[int] = None
    name: str

class RSVP(BaseModel):
    id: Optional[int] = None
    userId: int = Field(alias='user_id')
    eventId: int = Field(alias='event_id')
    status: Optional[str] = 'Attending'

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

# Create a new user profile or get all users
@app.post('/users', response_model=User, status_code=201)
def create_user(user: User):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (name) VALUES (%s)"
            cursor.execute(sql, (user.name,))
            connection.commit()
            user.id = cursor.lastrowid
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

@app.get('/users', response_model=List[User])
def get_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            users = cursor.fetchall()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

# RSVP to an event
@app.post('/rsvp', response_model=RSVP, status_code=201)
def rsvp_event(rsvp: RSVP):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO rsvps (user_id, event_id, status) VALUES (%s, %s, %s)"
            cursor.execute(sql, (rsvp.userId, rsvp.eventId, rsvp.status))
            connection.commit()
            rsvp.id = cursor.lastrowid
        return rsvp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

# Get user RSVPs
@app.get('/rsvp/user/{user_id}', response_model=List[RSVP])
def get_user_rsvps(user_id: int):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM rsvps WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            rsvps = cursor.fetchall()
        if rsvps:
            return rsvps
        else:
            raise HTTPException(status_code=404, detail="No RSVPs found for this user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

from typing import List

@app.get('/rsvp', response_model=List[RSVP])
def get_all_rsvps():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM rsvps"
            cursor.execute(sql)
            rsvps = cursor.fetchall()
        # Create RSVP instances using field aliases
        return [RSVP(**rsvp) for rsvp in rsvps]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connection.close()

# Run the application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host='0.0.0.0', port=5001)