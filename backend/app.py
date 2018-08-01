import os

from flask import Flask
from flask_cors import CORS

from database import migrate, db, User
from api import api


config_variable_name = 'FLASK_CONFIG_PATH'
default_config_path = os.path.join(os.path.dirname(__file__), 'config/local.py')
os.environ.setdefault(config_variable_name, default_config_path)


def create_app(config_file=None, settings_override=None):
    # yeap
    app = Flask(__name__)
    CORS(app)
    print(os.getenv('FLASK_CONFIG_PATH'))
    print(os.getenv('MATLAB_CPLEX_PATH'))

    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar(config_variable_name)

    if settings_override:
        app.config.update(settings_override)

    init_app(app)
    os.environ.setdefault('SECRET_KEY', app.config['SECRET_KEY'])
    os.environ.setdefault('HAMO_URL', app.config['HAMO_URL'])

    # if not production, then create an admin
    if os.getenv(config_variable_name) == default_config_path:
        check_or_create_admin(app)

    return app


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

def check_or_create_admin(app):
    username = 'admin'
    password = 'hamod'

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if user == None:
            print('WARN: Created admin user.')
            user=User(username, password)
            User.add(user)

    return
