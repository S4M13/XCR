from flask import render_template
from flask import make_response
from flask import request
from flask import flash
from flask import redirect
from flask import current_app
from flask import jsonify

if __name__ == "__main__":
    from ..App import Settings
    import Database
    import GlobalContext
else:
    import Settings
    from Util import Database
    from Util import GlobalContext

import time
import uuid
import base64
from typing import Optional
from functools import wraps
from sentry_sdk import configure_scope


def auth_required(level: int, api: bool = False, page: bool =True):
    """
    Ensures the accessing person has a session and the session has a **authentication level** above or equal to `level`

    :param level: The required level to access the endpoint
    :param api: If true, it returns a JSON error code rather than a 302 with an error message. Default is False
    :param page: If true, will record this in the users session as the last visited page. Not required if already
    indicated it is an endpoint.
    :return: A wrapper function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Fetch the session from the request
            if Settings.SESSION_COOKIE_NAME in request.cookies:
                raw_session_id = request.cookies[Settings.SESSION_COOKIE_NAME]
                session = Session.session_from_id(raw_session_id)
            else:
                session = None

            # Ensure page needs protection, ignore pages that don't require auth
            if level == 0:
                return func(session, *args, **kwargs)

            # If no valid session if found, send back to login page
            if session is None:
                if not api:
                    return redirect("/login", code=302)
                else:
                    return jsonify({'success': False, 'redir': '/login'})

            # If a valid session is found, update the last accessed
            session.update()

            # Check if session has timed out, if so redirect to login
            if session.created + Settings.SESSION_TIMEOUT < time.time():
                session.logout()
                current_app.logger.info(f"User '{session.name}'[ID:{session.raw_session_id}] attempted to access"
                                        f" a protected page, but their session had expired")

                if not api:
                    flash("Your session has expired, please log back in", "error")
                    return redirect("/login", code=302)
                else:
                    return jsonify({'success': False, 'redir': '/login'})

            # Check the current user has sufficient permissions to access the page
            if session.auth_level < level:
                current_app.logger.warning(f"{session} attempted to access '{func.__name__}' view with "
                                           f"insufficient permissions")

                flash("You do not have permission to access this page. If you believe this is an error please contact "
                      "an administrator.", "error")
                return redirect(session.last_visited)

            # All checks passed, configure the scope and respond with the request
            if (not api) and page:
                session.last_visited = request.path

            with configure_scope() as scope:
                scope.user = {"username": session.name,
                              "id": session.session_id,
                              "server": GlobalContext.SERVER_NAME}

                return func(session, *args, **kwargs)

        return wrapper

    return inner


def csrf_required(api: bool = False):
    """
    Ensures **anti-csrf-token** is passed along in a HTML POST form, and that the token matches the current session token.
    `If the given token is invalid, or no token is given then the session terminates.`


    :param api: If true, it returns a JSON error code rather than a 302 with an error message. Default is False

    :return: A wrapper function
    """

    def inner(func):

        @wraps(func)
        def wrapper(session, *args, **kwargs):
            # Check for a valid session
            if session is None or type(session) != Session:
                raise Exception("Cannot implement CSRF protection on something that does not require session "
                                "authentication of level 1 or above.")

            # Ensure the token has been passed successfully
            if "X-CSRF-TOKEN" in request.form:
                # Ensure token matches the stored token

                token = request.form["X-CSRF-TOKEN"]
                if token == session.raw_csrf_token:
                    return func(session, *args, **kwargs)

            # Else, invalidate the session and warn user of potential attack
            session.logout()

            current_app.logger.warning(f"{session} submitted an incorrect CSRF token, causing their session to expire")
            if not api:
                flash("Your session has been expired, please log back in.", "error")
                return redirect("/login", code=302)
            else:
                return jsonify({'success': False, 'redir': '/login'})

        return wrapper

    return inner


class Session:
    """Represents a current active session logged into the web app. Each session is associated with an account, under
    which the session has been authorized.

    The session object contains various information about the session as well as any associated session data. Decorating
    and endpoint with :meth:`auth_required` will result in any active session being passed along if one is found.

    :param name: The name of the associated account.
    :param auth_level: The authentication level of the associated account.
    :param auth_name: A user friendly representation of ``auth_level``. See :meth:`Session.auth_name_from_level`.
    :param id: A unique integer ID for each session
    :param session_id: A UUID for each session.
    :param raw_session_id: Base64 encoded version of `session_id`.
    :param csrf_token: The Anti-CSRF token for the current active session. Also a UUID.
    :param raw_csrf_token: Base64 encoded version of the `csrf_token`
    :param last_accessed: A UNIX timestamp of the last time this session accessed a page that checks authentication.
    param last_accessed: A UNIX timestamp of when the session was created
    :param session_data: A dictionary of which session data can be saved for persistence.
    """

    CURRENT_ACTIVE_SESSIONS = []

    def __init__(self, name: str, auth_level: int, ip: str) -> None:
        self.name = name
        self.auth_level = auth_level
        self.auth_name = Session.auth_name_from_level(self.auth_level)
        self.ip = ip

        self.id = Session.generate_unique_id()

        self.session_id = uuid.uuid4()
        self.raw_session_id = base64.urlsafe_b64encode(self.session_id.bytes).decode("utf-8")

        self.csrf_token = uuid.uuid4()
        self.raw_csrf_token = base64.urlsafe_b64encode(self.csrf_token.bytes).decode("utf-8")

        self.last_accessed = time.time()
        self.last_visited = "/"
        self.created = time.time()
        self.session_data = {}

        Session.CURRENT_ACTIVE_SESSIONS.append(self)

    def __repr__(self):
        return f"{self.name}[{self.session_id}::{self.ip}]"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def generate_unique_id(cls) -> int:
        """
        Generates a unique ID for each session by counting up from one until it finds a valid ID which is not already
        in use.

        :return: Returns the unique ID
        """
        current_ids = [s.id for s in cls.CURRENT_ACTIVE_SESSIONS]
        uid = 1

        while uid in current_ids:
            uid += 1

        return uid

    @staticmethod
    def valid_username(username: str) -> bool:
        """
        Checks if a given username exists in the database

        :param username: The username to check if it is valid or not
        :return: Either true or false, depending on if the session is valid or not
        """
        valid_entries = Database.User.query.filter_by(name=username).all()

        return len(valid_entries) > 0

    @staticmethod
    def login(username: str, password: str, ip: str) -> Optional['Session']:
        """
        Attempts to create a new session under the account associated with the given username and password. If the
        username or password is invalid, None is returned.

        :param username: The user's username
        :param password: The user's password
        :param ip: The IP of the user attempting to create the session
        :return: Either a session instance, or None
        """
        user_info = Database.User.query.filter_by(name=username).first()

        if user_info is None: return None

        if not user_info.check_password(password): return None

        new_session = Session(user_info.name, user_info.auth_level, ip)

        return new_session

    def logout(self) -> None:
        """
        Causes the session to logout, and remove itself from the list of active sessions.
        """
        Session.CURRENT_ACTIVE_SESSIONS.remove(self)

    def update(self) -> None:
        """
        Updates the last_accessed time stamp to the current UNIX time
        """
        self.last_accessed = time.time()

    @classmethod
    def session_from_id(cls, raw_session_id: str) -> Optional['Session']:
        """
        Attempts to fetch a session from a raw session id.

        :param raw_session_id: The **raw session id** to compare to.
        :return: Returns either a session if one was found, or None
        """
        for session in cls.CURRENT_ACTIVE_SESSIONS:
            if session.raw_session_id == raw_session_id:
                return session
        else:
            return None

    @staticmethod
    def auth_name_from_level(auth_level: int) -> str:
        """
        Takes the given **authentication level** and returns a user friendly representation

        :param auth_level: The auth_level to convert
        :return: A user friendly representation
        """
        if auth_level in Settings.PERMISSION_NAMES:
            return Settings.PERMISSION_NAMES[auth_level]
        else:
            return "Permission level {0}".format(auth_level)
