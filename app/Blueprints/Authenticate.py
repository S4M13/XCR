from flask import Blueprint
from flask import render_template
from flask import flash
from flask import make_response
from flask import redirect
from flask import current_app
from flask import request

if __name__ == "__main__":
    from ..Util import Auth
    from ..Util import Helper
    from ..Util import GlobalContext
    from ...app import Settings
else:
    from Util import Auth
    from Util import Helper
    from Util import GlobalContext
    import Settings

import datetime
import time

Authenticate = Blueprint("Authenticate", __name__)


@Authenticate.route("/login", methods=["GET"])
@Auth.auth_required(0)
def login(session):
    if session is not None:
        return redirect("/", code=302)

    return render_template("authenticate/login.html")


@Authenticate.route("/auth", methods=["POST"])
@Auth.auth_required(0, page=False)
@Helper.request_form("username", "password")
def auth(session, username, password):
    if session is not None:
        return redirect("/", code=302)

    if Auth.Session.valid_username(username):
        if username in GlobalContext.LOGIN_ATTEMPTS:
            last_time = GlobalContext.LOGIN_ATTEMPTS[username][0]
            current_attempts = GlobalContext.LOGIN_ATTEMPTS[username][1]

            if (time.time() - last_time) < Settings.MAX_LOGIN_ATTEMPT_PERIOD:
                if current_attempts >= Settings.MAX_LOGIN_ATTEMPTS:
                    flash("This account has been temporarily locked due to too many incorrect login attempts; please "
                          "try again later", "error")

                    current_app.logger.info(f"IP address [{request.remote_addr}] exceeded the maximum login attempts "
                                            f"for the '{username}' account and was temporarily blocked from logging "
                                            f"in")

                    return redirect("/login", code=302)
                else:
                    GlobalContext.LOGIN_ATTEMPTS[username] = (time.time(), current_attempts + 1)
            else:
                GlobalContext.LOGIN_ATTEMPTS[username] = (time.time(), 1)
        else:
            GlobalContext.LOGIN_ATTEMPTS[username] = (time.time(), 1)

    new_session = Auth.Session.login(username, password, request.remote_addr)

    if new_session is None:
        flash("Invalid username or password; Please try again", "error")

        current_app.logger.warning(f"Failed login attempt for user '{username}' [IP::{request.remote_addr}]")
        return redirect("/login", code=302)

    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(seconds=Settings.SESSION_TIMEOUT)

    resp = make_response(redirect("/", code=302))

    resp.set_cookie(Settings.SESSION_COOKIE_NAME,
                    new_session.raw_session_id,
                    samesite=Settings.COOKIE_SAME_SITE,
                    secure=Settings.COOKIE_SECURE,
                    expires=expire_date)

    GlobalContext.LOGIN_ATTEMPTS[username] = (time.time(), 0)

    current_app.logger.info(f"{new_session} successfully logged in")
    return resp


@Authenticate.route("/deauth", methods=["POST"])
@Auth.auth_required(1, page=False)
@Auth.csrf_required()
def deauth(session):
    session.logout()

    flash("Successfully logged out", "success")

    resp = make_response(redirect("/login", code=302))

    resp.set_cookie(Settings.SESSION_COOKIE_NAME,
                    "",
                    samesite="Lax",
                    secure=False,
                    expires=0)

    current_app.logger.info(f"{session} successfully logged out")
    return resp


@Authenticate.route("/")
@Auth.auth_required(1)
def base_dir(session):
    return Helper.render_base_template(session, "base/home.html")


@Authenticate.route("/unsupported")
def unsupported():
    return render_template("authenticate/unsupported.html")

