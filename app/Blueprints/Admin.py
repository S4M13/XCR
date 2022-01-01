from flask import Blueprint
from flask import flash
from flask import redirect
from flask import current_app
from flask import send_file
from flask import send_from_directory

if __name__ == "__main__":
    from ...app import Settings
    from ..Util import Auth
    from ..Util import Helper
    from ..Util import Database
    from ..Util import GlobalContext
else:
    import Settings
    from Util import Auth
    from Util import Helper
    from Util import Database
    from Util import GlobalContext

import datetime
import os

Admin = Blueprint("Admin", __name__)


@Admin.route("/users", methods=["GET"])
@Auth.auth_required(3)
def users(session):
    user_entries = Database.User.query.all()
    user_entries_sanitized = []

    for user in user_entries:
        user_entries_sanitized.append([user.id, user.name, Auth.Session.auth_name_from_level(user.auth_level)])

    return Helper.render_base_template(session, "admin/users.html", users=user_entries_sanitized)


@Admin.route("/delete_user", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("user-id")
def delete_user(session, user_id):
    user_entry = Database.User.query.filter_by(id=user_id).first()

    if user_entry is None:
        flash("Invalid user ID, that user does not exists", "error")
        return redirect("/users", code=302)

    if user_entry.name == session.name:
        flash("Cannot delete the user you are currently logged in as", "error")
        return redirect("/users", code=302)

    Database.db.session.delete(user_entry)
    Database.db.session.commit()

    for session in Auth.Session.CURRENT_ACTIVE_SESSIONS:
        if session.name == user_entry.name:
            session.logout()

    current_app.logger.info(f"{session} deleted User {user_entry.name}[ID:{user_id}]")

    flash("Successfully deleted the user", "success")
    return redirect("/users", code=302)


@Admin.route("/create_user", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("username", "password", "auth-level")
def create_user(session, username, password, auth_level):
    try:
        int(auth_level)
    except ValueError:
        flash("The access level must be a number, please select one of the options from the list", "error")
        return redirect("/users", code=302)

    check = Database.User.query.filter_by(name=username).first()
    if check is not None:
        flash("An account already exists with this username, please select another", "error")
        return redirect("/users", code=302)

    new_user = Database.User(name=username, auth_level=auth_level)
    new_user.set_password(password)

    Database.db.session.add(new_user)
    Database.db.session.commit()

    current_app.logger.info(f"{session} created User {username}[ID:{new_user.id}]")

    flash("Successfully created a new user", "success")
    return redirect("/users", code=302)


@Admin.route("/logs", methods=["GET"])
@Auth.auth_required(3)
def logs(session):
    data = []
    logs = os.listdir(Settings.LOG_FILE_DIRECTORY)
    for entry in logs:
        if ".log" in entry:
            loc = os.path.join(Settings.LOG_FILE_DIRECTORY, entry)
            data.append([entry,
                         loc,
                         datetime.datetime.fromtimestamp(os.path.getmtime(loc)).strftime('%Y-%m-%d %H:%M:%S'),
                         f"{os.path.getsize(loc) / 1000} KB"])

    return Helper.render_base_template(session, "admin/logs.html", data=data)


@Admin.route("/download_log_file", methods=["GET"])
@Auth.auth_required(3, page=False)
@Helper.request_args("file")
def download_log_file(session, filename):
    location = os.path.join(Settings.LOG_FILE_DIRECTORY, filename)
    location = os.path.abspath(location)

    if not Helper.is_safe_path(os.path.abspath(Settings.LOG_FILE_DIRECTORY), location):
        current_app.logger.warning(f"{session} attempted to download a logfile from an unsafe path['{location}']"
                                   f"[Raw Query:'{filename}']")

        flash("Failed to find the log file to download", "error")
        return redirect("/logs", code=302)

    if not os.path.exists(location):
        flash("Failed to find the log file to download", "error")
        return redirect("/logs", code=302)

    current_app.logger.info(f"{session} downloaded '{location}' from the log files")

    timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    return send_file(location, mimetype='text/plain', attachment_filename=f"{timestamp}.log", as_attachment=True)


@Admin.route("/delete_log_file", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("file-name")
def delete_log_file(session, filename):
    location = os.path.join(Settings.LOG_FILE_DIRECTORY, filename)
    location = os.path.abspath(location)

    if not Helper.is_safe_path(os.path.abspath(Settings.LOG_FILE_DIRECTORY), location):
        current_app.logger.warning(f"{session} attempted to delete a logfile from an unsafe path['{location}']"
                                   f"[Raw Query:'{filename}']")

        flash("Failed to find the log file to delete", "error")
        return redirect("/logs", code=302)

    try:
        os.remove(location)
    except PermissionError:
        current_app.logger.warning(f"{session} attempted to delete a logfile but a PermissionError "
                                   f"occurred['{location}'][Raw Query:'{filename}'] - "
                                   f"the file is likely the active log file")
        flash("Cannot delete this log file as it is currently being used", "error")
        return redirect("/logs", code=302)

    except FileNotFoundError:
        current_app.logger.warning(f"{session} attempted to delete a log file but the log file doesn't exist. It is "
                                   f"likely a client side error has occured, or a deliberate action has been taken to"
                                   f" alter the path.")

        flash("Cannot delete this log file as it does not exist.", "error")
        return redirect("/logs", code=302)

    current_app.logger.info(f"{session} deleted '{location}' from the log files")

    flash("Successfully deleted the log file", "success")
    return redirect("/logs", code=302)


@Admin.route("/sessions", methods=["GET"])
@Auth.auth_required(3)
def sessions(session):
    sessions = []

    for session in Auth.Session.CURRENT_ACTIVE_SESSIONS:
        created_at_timestamp = datetime.datetime.fromtimestamp(session.created).strftime("%Y-%m-%d %H:%M:%S")
        last_accessed_timestamp = datetime.datetime.fromtimestamp(session.last_accessed).strftime("%Y-%m-%d %H:%M:%S")
        sessions.append([session.name,
                         session.auth_name,
                         created_at_timestamp,
                         last_accessed_timestamp,
                         session.id])

    return Helper.render_base_template(session, "admin/sessions.html", sessions=sessions)


@Admin.route("/terminate_session", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("session-id")
def terminate_session(session, session_id):
    terminated_session = None
    for s in Auth.Session.CURRENT_ACTIVE_SESSIONS:
        if str(s.id) == session_id:
            s.logout()
            terminated_session = s
            break
    else:
        current_app.logger.warning(f"{session} attempted to terminate session with ID '{session_id}' but no session "
                                   f"exists with this internal ID")
        flash("Cannot find a session with the given session ID to terminate", "error")
        return redirect("/sessions", code=302)

    current_app.logger.info(f"{session} terminated session {terminated_session} [Internal ID : {session_id}]")
    flash("Successfully terminated the session", "success")
    return redirect("/sessions", code=302)


@Admin.route("/data", methods=["GET"])
@Auth.auth_required(3)
def data(session):
    student_datastores = []

    files = os.listdir(Settings.STUDENT_DATASTORE_LOCATION)
    files.sort()
    for index, file in enumerate(files):
        if file[-5:] == ".xlsx":
            data_point = [index, file]
            if file in GlobalContext.STUDENTS_DATASTORE.loaded_sheet_names:
                data_point.append("Yes")
            else:
                data_point.append("No")
            student_datastores.append(data_point)

    club_datastores = []

    files = os.listdir(Settings.CLUBS_DATASTORE_LOCATION)
    files.sort()
    for index, file in enumerate(files):
        if file[-5:] == ".xlsx":
            data_point = [index, file]
            if file in GlobalContext.CLUBS_DATASTORE.loaded_sheet_names:
                data_point.append("Yes")
            else:
                data_point.append("No")
            club_datastores.append(data_point)

    return Helper.render_base_template(session,
                                       "admin/data.html",
                                       student_datastores=student_datastores,
                                       club_datastores=club_datastores)


@Admin.route("/download_student_datastore", methods=["GET"])
@Auth.auth_required(3, page=False)
@Helper.request_args("id")
def download_student_datastore(session, id_uf):
    try:
        ID = int(id_uf)
    except ValueError:
        flash("Invalid ID submitted - failed to download datastore", "error")
        return redirect("/data", code=302)

    files = os.listdir(Settings.STUDENT_DATASTORE_LOCATION)
    files.sort()

    try:
        file = files[ID]
    except IndexError:
        flash("Invalid ID submitted - failed to download datastore", "error")
        return redirect("/data", code=302)

    current_app.logger.info(f"{session} downloaded the student datastore file '{file}'")

    return send_from_directory(Settings.STUDENT_DATASTORE_LOCATION, file, attachment_filename=file, as_attachment=True)


@Admin.route("/download_club_datastore", methods=["GET"])
@Auth.auth_required(3, page=False)
@Helper.request_args("id")
def download_club_datastore(session, id_uf):
    try:
        ID = int(id_uf)
    except ValueError:
        flash("Invalid ID submitted - failed to download datastore", "error")
        return redirect("/data", code=302)

    files = os.listdir(Settings.CLUBS_DATASTORE_LOCATION)
    files.sort()

    try:
        file = files[ID]
    except IndexError:
        flash("Invalid ID submitted - failed to download datastore", "error")
        return redirect("/data", code=302)

    current_app.logger.info(f"{session} downloaded the club datastore file '{file}'")

    return send_from_directory(Settings.CLUBS_DATASTORE_LOCATION, file, attachment_filename=file, as_attachment=True)


@Admin.route("/delete_student_datastore", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("datastore-id")
def delete_student_datastore(session, id_uf):
    try:
        ID = int(id_uf)
    except ValueError:
        flash("Invalid ID submitted - failed to delete datastore", "error")
        return redirect("/data", code=302)

    files = os.listdir(Settings.STUDENT_DATASTORE_LOCATION)
    files.sort()

    try:
        file = files[ID]
    except IndexError:
        flash("Invalid ID submitted - failed to delete datastore", "error")
        return redirect("/data", code=302)

    location = os.path.join(Settings.STUDENT_DATASTORE_LOCATION, file)
    try:
        os.remove(location)
    except PermissionError:
        flash("An unknown error occurred - failed to delete the datastore")
        return redirect("/data", code=302)

    GlobalContext.STUDENTS_DATASTORE.purge_memory()
    GlobalContext.STUDENTS_DATASTORE.load_directory(Settings.STUDENT_DATASTORE_LOCATION)

    current_app.logger.info(f"{session} deleted the student datastore file '{file}'")

    flash("Successfully deleted datastore", "success")
    return redirect("/data", code=302)


@Admin.route("/delete_club_datastore", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
@Helper.request_form("datastore-id")
def delete_club_datastore(session, id_uf):
    try:
        ID = int(id_uf)
    except ValueError:
        flash("Invalid ID submitted - failed to delete datastore", "error")
        return redirect("/data", code=302)

    files = os.listdir(Settings.CLUBS_DATASTORE_LOCATION)
    files.sort()

    try:
        file = files[ID]
    except IndexError:
        flash("Invalid ID submitted - failed to delete datastore", "error")
        return redirect("/data", code=302)

    location = os.path.join(Settings.CLUBS_DATASTORE_LOCATION, file)
    try:
        os.remove(location)
    except PermissionError:
        flash("An unknown error occurred - failed to delete the datastore")
        return redirect("/data", code=302)

    GlobalContext.CLUBS_DATASTORE.purge_memory()
    GlobalContext.CLUBS_DATASTORE.load_directory(Settings.CLUBS_DATASTORE_LOCATION)

    current_app.logger.info(f"{session} deleted the club datastore file '{file}'")

    flash("Successfully deleted datastore", "success")
    return redirect("/data", code=302)


@Admin.route("/reload_student_datastore", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
def reload_student_datastore(session):
    GlobalContext.STUDENTS_DATASTORE.purge_memory()
    GlobalContext.STUDENTS_DATASTORE.load_directory(Settings.STUDENT_DATASTORE_LOCATION)

    current_app.logger.info(f"{session} reloaded the student datastore")

    flash("Successfully reloaded student datastore", "success")
    return redirect("/data", code=302)


@Admin.route("/reload_club_datastore", methods=["POST"])
@Auth.auth_required(3, page=False)
@Auth.csrf_required()
def reload_club_datastore(session):
    GlobalContext.CLUBS_DATASTORE.purge_memory()
    GlobalContext.CLUBS_DATASTORE.load_directory(Settings.CLUBS_DATASTORE_LOCATION)

    current_app.logger.info(f"{session} reloaded the club datastore")

    flash("Successfully reloaded club datastore", "success")
    return redirect("/data", code=302)

