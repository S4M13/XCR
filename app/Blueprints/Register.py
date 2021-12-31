from flask import Blueprint
from flask import request
from flask import jsonify

if __name__ == "__main__":
    from ..Util import Auth
    from ..Util import Helper
    from ..Util import GlobalContext
    from ..Util import Database
else:
    from Util import Auth
    from Util import Helper
    from Util import GlobalContext
    from Util import Database

import datetime

Register = Blueprint("Register", __name__)


@Register.route("/register_one", methods=["GET"])
@Auth.auth_required(1)
def register_one(session):
    return Helper.render_base_template(session, "register/register_one.html")


@Register.route("/register_one_form", methods=["POST"])
@Auth.auth_required(1, api=True)
@Auth.csrf_required()
@Helper.request_form("name", "name-id", "club", "club-id", "date")
@Helper.ensure_valid_student_id(2, api=True)
@Helper.ensure_valid_club_id(4, api=True)
def register_one_form(session, student, student_id, club, club_id, date):
    student_entry = GlobalContext.STUDENTS_DATASTORE.return_specific_entries("UID", student_id)[0]
    student_entry_name = student_entry[1] + " " + student_entry[2]

    club_entry = GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_id)[0]

    if not (student == student_entry_name):
        data = {"success": False,
                "error": "Student name doesn't match the given ID in internal records - please contact a"
                         " network administrator"}

        return jsonify(data)

    if not (club == club_entry[1]):
        data = {"success": False,
                "error": "Club name doesn't match the given ID in internal records - please contact a"
                         " network administrator"}

        return jsonify(data)

    try:
        register_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        data = {"success": False,
                "error": "The entered date is not valid. Must be in the format YYYY-MM-DD or be a selected date from "
                         "the calender"}

        return jsonify(data)

    try:
        new_record = Database.Record(student_uid=student_id, club_uid=club_id, attendance_date=register_date)
        Database.db.session.add(new_record)
        Database.db.session.commit()
    except Exception as e:
        data = {"success": False,
                "error": "Something has gone wrong, please contact the network administrator"}

        return jsonify(data)

    data = {"success": True}
    return jsonify(data)


@Register.route("/register_class", methods=["GET"])
@Auth.auth_required(1)
def register_class(session):
    if "persistent_register_ids" in session.session_data.keys():
        persistent_register = zip(session.session_data["persistent_register_ids"],
                                  session.session_data["persistent_register_names"])

        length = len(session.session_data["persistent_register_names"])
    else:
        persistent_register = []
        length = 0

    return Helper.render_base_template(session,
                                       "register/register_class.html",
                                       persistent_register=persistent_register,
                                       length=length)


@Register.route("/register_class_form", methods=["POST"])
@Auth.auth_required(1, api=True)
@Auth.csrf_required()
@Helper.request_form("club", "club-id", "date")
@Helper.ensure_valid_club_id(2, api=True)
def register_class_form(session, club, club_id, date):
    students_uf = request.form.getlist("students[]")
    student_ids_uf = request.form.getlist("student-ids[]")

    students = []
    student_ids = []

    for student, student_id in zip(students_uf, student_ids_uf):
        if student_id not in student_ids:
            students.append(student)
            student_ids.append(student_id)

    for student, student_id in zip(students, student_ids):
        student_entry_records = GlobalContext.STUDENTS_DATASTORE.return_specific_entries("UID", student_id)

        if len(student_entry_records) != 1:
            data = {"success": False,
                    "error": f"Failed to register {student} as given ID is not a valid ID within the database "
                             f"records - please contact a network administrator. "
                    }

            return jsonify(data)

        student_entry = student_entry_records[0]
        student_entry_name = student_entry[1] + " " + student_entry[2]

        if not (student == student_entry_name):
            data = {"success": False,
                    "error": f"Failed to register {student} as given name doesn't match the given ID in internal "
                             f"records - please contact a network administrator. "
                    }

            return jsonify(data)

    club_entry = GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_id)[0]
    if not (club == club_entry[1]):
        data = {"success": False,
                "error": "Club name doesn't match the given ID in internal records - please contact a"
                         " network administrator"}

        return jsonify(data)

    try:
        register_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        data = {"success": False,
                "error": "The entered date is not valid. Must be in the format YYYY-MM-DD or be a selected date from "
                         "the calender"}

        return jsonify(data)

    try:
        for student_id in student_ids:
            new_record = Database.Record(student_uid=student_id, club_uid=club_id, attendance_date=register_date)
            Database.db.session.add(new_record)

        Database.db.session.commit()
    except Exception as e:
        data = {"success": False,
                "error": "Something has gone wrong, please contact the network administrator or try again later."}

        return jsonify(data)

    return jsonify({"success": True})


@Register.route("/view_records", methods=["GET"])
@Auth.auth_required(1)
def view_records(session):
    return Helper.render_base_template(session, "register/view_records.html")
