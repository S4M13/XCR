from flask import Blueprint
from flask import render_template
from flask import flash
from flask import make_response
from flask import redirect
from flask import request
from flask import url_for
from flask import current_app

from werkzeug.exceptions import InternalServerError
from sentry_sdk import last_event_id

Handler = Blueprint("Handler", __name__)


@Handler.app_errorhandler(500)
def handle_500(e):
    return render_template("handler/500.html", sentry_event_id=last_event_id()), 500


@Handler.app_errorhandler(404)
def handle_404(e):
    return render_template("handler/404.html"), 404
