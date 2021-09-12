from sqlalchemy.orm import Session
from datetime import datetime

AVAILABLE_TAGS = ["fragile", "dangerous"]

# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into database
def insert_into_db(obj, db):
    with Session(db) as session:
        try:
            session.add(obj)
        except:
            session.rollback()
            raise
        else:
            session.commit()


# Clear session data
def clear_session(session):
    for key in [key for key in session]:
        session.pop(key, None)
