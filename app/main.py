from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import g

from jinja2 import Environment, select_autoescape
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.tornado import TornadoIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os
import json

from Util import Datastore
from Util import Auth
from Util import Helper
from Util.GlobalContext import GlobalContext
from Util import Database

from Blueprints.Authenticate import Authenticate
from Blueprints.Register import Register
from Blueprints.Admin import Admin
from Blueprints.API import API
from Blueprints.Handler import Handler
from Blueprints.Analysis import Analysis

from Config import Config
import Settings

# Fetch config information
with open(Settings.SERVER_CONFIG) as fp:
    GlobalContext.CONFIG = json.load(fp)

# Attempt to fetch server name
GlobalContext.SERVER_NAME = "Anonymous"

if GlobalContext.CONFIG.get('server_name') is not None:
    GlobalContext.SERVER_NAME = GlobalContext.CONFIG.get("server_name")

# Config Sentry SDK
"""
sentry_sdk.init(
    release="xcr-register@" + Settings.CURRENT_VERSION,
    server_name=GlobalContext.SERVER_NAME,
    attach_stacktrace=True,
    dsn="https://856572d34eac4df094ae709f46bee757@o418385.ingest.sentry.io/5320913",
    integrations=[FlaskIntegration(), TornadoIntegration(), SqlalchemyIntegration()]
    )
"""

# Init Flask APP
app = Flask(__name__)
app.config.from_object(Config)

# Init DB
Database.db.init_app(app)

# Init Logger
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = RotatingFileHandler(Settings.LOG_FILE_LOCATION, maxBytes=5000000, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Register Blueprints
app.register_blueprint(Authenticate)
app.register_blueprint(Register)
app.register_blueprint(Admin)
app.register_blueprint(API)
app.register_blueprint(Handler)
app.register_blueprint(Analysis)

# Config Jinja2 Env
env = Environment(autoescape=select_autoescape(
    disabled_extensions=('txt',),
    default_for_string=True,
    default=True,
))

# Init datastore
TEMP_DS = Datastore.Datastore()
TEMP_DS.load_directory(Settings.CLUBS_DATASTORE_LOCATION)
GlobalContext.CLUBS_DATASTORE = TEMP_DS

TEMP_DS = Datastore.Datastore()
TEMP_DS.load_directory(Settings.STUDENT_DATASTORE_LOCATION)
GlobalContext.STUDENTS_DATASTORE = TEMP_DS
if __name__ == "__main__":
    # Create an debug session
    debug_session = Auth.Session("DEBUG", 999, '0.0.0.0')
    debug_session.raw_session_id = "DEBUG"

    x = lambda: app.logger.info("Overriding DEBUG session logout")
    debug_session.logout = x

    app.run('0.0.0.0', 80, debug=True)
