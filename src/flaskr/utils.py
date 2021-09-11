from datetime import datetime
from sqlite3 import IntegrityError

AVAILABLE_TAGS = ["fragile", "dangerous"]

# Retrieves current timestamp
def timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


# Inserts object into database
def insert_into_db(obj, db):
    try:
        db.session.add(obj)
    except:
        db.session.rollback()
        raise IntegrityError
    db.session.commit()


# Clear session data
def clear_session(session):
    for key in [key for key in session]:
        session.pop(key, None)
