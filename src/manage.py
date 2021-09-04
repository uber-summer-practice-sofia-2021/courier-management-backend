import sys
from flaskr.models import *

def create_db():
    db.create_all()

if __name__ == "__main__":
    try:
        for i in range(1, len(sys.argv)):
            globals()[sys.argv[i]]()
    except KeyError as err:
        print(err)