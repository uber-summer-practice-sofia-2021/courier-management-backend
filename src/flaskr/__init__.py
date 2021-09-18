from flask import Flask
from flaskr.database.models import db
from datetime import timedelta
import os


# Application factory
def create_app(test_config=None):

    db_dialect = os.getenv('DATABASE_DIALECT')
    db_driver = os.getenv('DATABASE_DRIVER')
    db_path = os.getenv('DATABASE_PATH')
    db_username = os.getenv('DATABASE_USERNAME')
    db_passwd = os.getenv('DATABASE_PASSWD')
    db_host = os.getenv('DATABASE_HOST')
    db_port = os.getenv('DATABASE_PORT')

    app = Flask(__name__, instance_relative_config=True)
    app.permanent_session_lifetime = timedelta(minutes=30)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"{db_dialect}{f'+{db_driver}' if db_driver else ''}://{db_username+':'+db_passwd+'@'+db_host+':'+db_port if db_dialect != 'sqlite' else ''}/{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="de42fa9807694a272bc16aa52a1f8c8fa1b3fb1921cba6489f782dc476310de8",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from flaskr.user.routes import user
    from flaskr.api.routes import api
    from flaskr.main.routes import main

    app.register_blueprint(user)
    app.register_blueprint(api)
    app.register_blueprint(main)

    return app
