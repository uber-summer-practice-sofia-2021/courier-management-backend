import sys
from flaskr.database.models import *
import flaskr

# Removes all the tables in the db
def drop_db():
    with flaskr.create_app().app_context():
        db.drop_all()
    print("Database cleared")


# Creates tables in the db based on the imported models
def create_db():
    with flaskr.create_app().app_context():
        db.create_all()
    print("Database created")


if __name__ == "__main__":
    try:
        for i in range(1, len(sys.argv)):
            globals()[sys.argv[i]]()
    except KeyError as err:
        print(err)
