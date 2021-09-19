import sys, subprocess, app, os
from app.db.models import *

# Removes all the tables in the db
def drop_db():
    with app.create_app().app_context():
        db.drop_all()
    print("Database cleared")


# Creates tables in the db based on the imported models
def create_db():
    with app.create_app().app_context():
        db.create_all()
    print("Database created")


if __name__ == "__main__":
    for var in subprocess.Popen("egrep '([A-Z_]+)=([^ ]*)' ../Dockerfile -o", shell=True, stdout=subprocess.PIPE).stdout.readlines():
        var = var.decode('utf-8')[:-1]
        os.environ[var[:var.find("=")]]=var[var.find("=")+1:]

    try:
        for i in range(1, len(sys.argv)):
            globals()[sys.argv[i]]()
    except KeyError as err:
        print(err)
