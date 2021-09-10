from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.permanent_session_lifetime=timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database/server.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'de42fa9807694a272bc16aa52a1f8c8fa1b3fb1921cba6489f782dc476310de8'
db = SQLAlchemy(app)

from flaskr import routes