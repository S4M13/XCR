from flask import Blueprint
from flask import request
from flask import current_app
from flask import jsonify

if __name__ == "__main__":
    from ...app import Settings
    from ..Util import Auth
    from ..Util import Helper
    from ..Util import GlobalContext
    from ..Util import Database
else:
    import Settings
    from Util import Auth
    from Util import Helper
    from Util import GlobalContext
    from Util import Database

import functools
from functools import wraps
import time
import datetime

API = Blueprint("API", __name__, url_prefix="/api")


@API.route("/names", methods=["GET"])
@Auth.auth_required(1, api=True)
@Helper.request_args("query")
def names(session, query):
    if len(query) < 3:
        current_app.logger.warning(f"{session} submitted an API request to '/api/names' and the 'query' field was under"
                                   f" 3 characters long (Query : '{query}')")

        return "Invalid request"

    data = {"query": "Unit"}

    matches = []
    for d in GlobalContext.STUDENTS_DATASTORE.data:
        name = (d[1] + " " + d[2])
        if request.args["query"].lower() in name.lower():
            matches.append({"value": name, "data": d[0]})

    data["suggestions"] = matches
    return jsonify(data)


@API.route("/clubs", methods=["GET"])
@Auth.auth_required(1, api=True)
@Helper.request_args("query")
def clubs(session, query):
    data = {"query": "Unit"}

    matches = []
    for d in GlobalContext.CLUBS_DATASTORE.data:
        name = d[1]
        if query.lower() in name.lower():
            matches.append({"value": name, "data": d[0]})

    data["suggestions"] = matches
    return jsonify(data)


@API.route("/overall/weekly-attendance", methods=["GET"])
@Auth.auth_required(2, api=True)
def overall_weekly_attendance(session):
    return GlobalContext.DATABASE_ANALYSIS["overall_weekly_attendance"]


@API.route("/overall/weekly-attendance-by-club", methods=["GET"])
@Auth.auth_required(2, api=True)
def overall_weekly_attendance_by_club(session):
    return GlobalContext.DATABASE_ANALYSIS["overall_weekly_attendance_by_club"]


@API.route("/overall/club-breakdown", methods=["GET"])
@Auth.auth_required(2, api=True)
def club_breakdown(session):
    return GlobalContext.DATABASE_ANALYSIS["club_breakdown"]


@API.route("/overall/weekly-attendance-once", methods=["GET"])
@Auth.auth_required(2, api=True)
def overall_weekly_attendance_once(session):
    return GlobalContext.DATABASE_ANALYSIS["overall_weekly_attendance_once"]


@API.route("/overall/flash-cards", methods=["GET"])
@Auth.auth_required(2, api=True)
def flash_cards(session):
    return GlobalContext.DATABASE_ANALYSIS["flash_cards"]


@API.route("/student/fetch_records", methods=["GET"])
@Auth.auth_required(1, api=True)
@Helper.request_args("student-id")
@Helper.ensure_valid_student_id(1, api=True)
def fetch_records(session, student_uid):
    records = Database.Record.query.filter_by(student_uid=student_uid).all()

    data = []
    for record in records:
        iso_stamp = record.attendance_date.isocalendar()
        weekly_stamp = f"{str(iso_stamp[1]).zfill(2)}-{iso_stamp[0]}"

        strf_time = record.attendance_date.strftime("%Y-%m-%d %H:%M:%S")
        club_name = GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", record.club_uid)[0][1]

        data.append((weekly_stamp, strf_time, club_name, record.club_uid))

    data.sort(key=functools.cmp_to_key(Helper.smart_comp), reverse=True)

    response = {"success": True, "data": data}
    return jsonify(response)


@API.route("/student/delete_record", methods=["POST"])
@Auth.auth_required(1, api=True)
@Auth.csrf_required(api=True)
@Helper.request_form("student-id", "club-id", "timestamp")
def delete_record(session, student_uid, club_uid, timestamp):

    ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    matches = Database.Record.query.filter_by(student_uid=student_uid,
                                              club_uid=club_uid,
                                              attendance_date=ts).all()

    if len(matches) == 0:
        return {"success": False, "error": "No entry found in the database for this student, club, and time."}

    for match in matches:
        Database.db.session.delete(match)

    Database.db.session.commit()

    return {"success": True}


@API.route("/student/weekly-attendance", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("name", "name-id")
@Helper.ensure_valid_student_id(2, api=True)
def student_weekly_attendance(session, name, student_uid):
    records = Database.Record.query.filter_by(student_uid=student_uid).all()

    attendance_analysis = {}
    for entry in records:
        iso_stamp = entry.attendance_date.isocalendar()
        weekly_stamp = f"{str(iso_stamp[1]).zfill(2)}-{iso_stamp[0]}"  # Get the weekly stamp for the record

        if weekly_stamp in attendance_analysis.keys():
            attendance_analysis[weekly_stamp] += 1
        else:
            attendance_analysis[weekly_stamp] = 1

    attendance_analysis = list(attendance_analysis.items())
    attendance_analysis.sort(key=functools.cmp_to_key(Helper.smart_comp))

    attendance_analysis = Helper.week_filler_analysis(attendance_analysis)

    attendance_analysis_formatting = {}
    attendance_analysis_formatting["success"] = True
    attendance_analysis_formatting["labels"] = [entry[0] for entry in attendance_analysis]
    attendance_analysis_formatting["datasets"] = [
        {"label": "Weekly Attendance",
         "backgroundColor": "rgb(12, 99, 255)",
         "borderColor": "rgb(12, 99, 255)",
         "data": [entry[1] for entry in attendance_analysis],
         "fill": False,
         "cubicInterpolationMode": "monotone"
         }
    ]

    return attendance_analysis_formatting


@API.route("/student/club-breakdown", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("name", "name-id")
@Helper.ensure_valid_student_id(2, api=True)
def student_club_breakdown(session, name, student_uid):
    records = Database.Record.query.filter_by(student_uid=student_uid).all()

    club_breakdown_analysis = {}
    for entry in records:
        if entry.club_uid in club_breakdown_analysis.keys():
            club_breakdown_analysis[entry.club_uid] += 1
        else:
            club_breakdown_analysis[entry.club_uid] = 1

    club_breakdown_analysis_formatting = {}
    club_breakdown_analysis_formatting["success"] = True
    club_breakdown_analysis_formatting["labels"] = [
        GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_uid)[0][1]
        for club_uid in club_breakdown_analysis.keys()
    ]

    club_breakdown_analysis_formatting["datasets"] = [
        {"label": "Club Attendance Distribution",
         "backgroundColor": ['#%02x%02x%02x' % (color[0], color[1], color[2])
                             for color in Helper.generate_distinct_colors(len(club_breakdown_analysis.items()))],
         "data": [data for data in club_breakdown_analysis.values()]
         }
    ]

    return club_breakdown_analysis_formatting


@API.route("/student/club-bar-chart", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("name", "name-id")
@Helper.ensure_valid_student_id(2, api=True)
def student_club_bar_chart(session, name, student_uid):
    records = Database.Record.query.filter_by(student_uid=student_uid).all()

    club_breakdown_analysis = {}
    for entry in records:
        if entry.club_uid in club_breakdown_analysis.keys():
            club_breakdown_analysis[entry.club_uid] += 1
        else:
            club_breakdown_analysis[entry.club_uid] = 1

    club_breakdown_analysis_formatting = {}
    club_breakdown_analysis_formatting["success"] = True
    club_breakdown_analysis_formatting["labels"] = [
        GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_uid)[0][1]
        for club_uid in club_breakdown_analysis.keys()
    ]

    club_breakdown_analysis_formatting["datasets"] = [
        {"label": "Club Attendance Distribution",
         "barPercentage": 0.5,
         "barThickness": 6,
         "maxBarThickness": 8,
         "minBarLength": 2,
         "backgroundColor": ['#%02x%02x%02x' % (color[0], color[1], color[2])
                             for color in Helper.generate_distinct_colors(len(club_breakdown_analysis.items()))],
         "data": [data for data in club_breakdown_analysis.values()]
         }
    ]

    return club_breakdown_analysis_formatting


@API.route("/student/flash-cards", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("name", "name-id")
@Helper.ensure_valid_student_id(2, api=True)
def student_flash_cards(session, name, student_uid):
    records = Database.Record.query.filter_by(student_uid=student_uid).all()

    clubs = {}
    for entry in records:
        if entry.club_uid not in clubs.keys():
            clubs[entry.club_uid] = 1
        else:
            clubs[entry.club_uid] += 1

    five_plus = 0
    for times in clubs.values():
        if times >= 5:
            five_plus += 1

    flash_cards = {
        "success": True,
        "one": len(records),
        "two": len(clubs.items()),
        "three": five_plus,
        "name": name
    }

    return flash_cards


@API.route("/club/weekly-attendance", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("club", "club-id")
@Helper.ensure_valid_club_id(1, api=True)
def club_weekly_attendance(session, club, club_uid):
    records = Database.Record.query.filter_by(club_uid=club_uid).all()
    attendance_analysis = {}
    for entry in records:
        iso_stamp = entry.attendance_date.isocalendar()
        weekly_stamp = f"{str(iso_stamp[1]).zfill(2)}-{iso_stamp[0]}"  # Get the weekly stamp for the record

        if weekly_stamp in attendance_analysis.keys():
            attendance_analysis[weekly_stamp] += 1
        else:
            attendance_analysis[weekly_stamp] = 1

    attendance_analysis = list(attendance_analysis.items())
    attendance_analysis.sort(key=functools.cmp_to_key(Helper.smart_comp))

    attendance_analysis = Helper.week_filler_analysis(attendance_analysis)

    attendance_analysis_formatting = {}
    attendance_analysis_formatting["success"] = True
    attendance_analysis_formatting["labels"] = [entry[0] for entry in attendance_analysis]
    attendance_analysis_formatting["datasets"] = [
        {"label": "Weekly Attendance",
         "backgroundColor": "rgb(12, 99, 255)",
         "borderColor": "rgb(12, 99, 255)",
         "data": [entry[1] for entry in attendance_analysis],
         "fill": False,
         "cubicInterpolationMode": "monotone"
         }
    ]

    return attendance_analysis_formatting


@API.route("/club/flash-cards", methods=["GET"])
@Auth.auth_required(2, api=True)
@Helper.request_args("club", "club-id")
@Helper.ensure_valid_club_id(1, api=True)
def club_flash_cards(session, club, club_uid):
    records = Database.Record.query.filter_by(club_uid=club_uid).all()

    students = {}
    weeks = []
    for entry in records:
        weekly_stamp = entry.attendance_date.strftime("%W-%Y")

        if entry.student_uid not in students.keys():
            students[entry.student_uid] = 1
        else:
            students[entry.student_uid] += 1
            
        if weekly_stamp not in weeks:
            weeks.append(weekly_stamp)

    five_plus = 0
    for times in students.values():
        if times >= 5:
            five_plus += 1

    flash_cards = {
        "success": True,
        "one": len(records),
        "two": five_plus,
        "three": len(weeks),
        "name": club
    }

    return flash_cards


@API.route("/session/persistent-register", methods=["GET"])
@Auth.auth_required(1, api=True)
def persistent_register(session):
    student_ids = request.args.getlist("student-ids[]")
    students = request.args.getlist("students[]")

    session.session_data["persistent_register_ids"] = student_ids
    session.session_data["persistent_register_names"] = students

    return jsonify({"success": True})