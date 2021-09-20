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
    # for var in subprocess.Popen("egrep '([A-Z_]+)=([^ ]*)' ../Dockerfile -o", shell=True, stdout=subprocess.PIPE).stdout.readlines():
    #     var = var.decode('utf-8')[:-1]
    #     os.environ[var[:var.find("=")]]=var[var.find("=")+1:]

    os.environ['FLASK_ENV']='development'
    os.environ['FLASK_APP']='src/app'
    os.environ['ORDER_MANAGEMENT_HOST']='localhost'
    os.environ['ORDER_MANAGEMENT_PORT']='5000'
    os.environ['KAFKA_BROKERS']="kafka:9092"
    os.environ['KAFKA_TOPIC']="trips"
    os.environ['DATABASE_HOST']=''
    os.environ['DATABASE_PORT']=''
    os.environ['DATABASE_USERNAME']=''
    os.environ['DATABASE_PASSWD']=''
    os.environ['DATABASE_PATH']='db/server.db'
    os.environ['DATABASE_DIALECT']='sqlite'
    os.environ['DATABASE_DRIVER']=''

    try:
        for i in range(1, len(sys.argv)):
            globals()[sys.argv[i]]()
    except KeyError as err:
        print(err)
