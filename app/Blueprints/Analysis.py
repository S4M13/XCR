from flask import Blueprint
from flask import flash
from flask import redirect
from flask import current_app
from flask import send_from_directory

if __name__ == "__main__":
    from ...app import Settings
    from ..Util import Auth
    from ..Util import Helper
    from ..Util import Generator
    from ..Util import GlobalContext
else:
    import Settings
    from Util import Auth
    from Util import Helper
    from Util import Generator
    from Util import GlobalContext

Analysis = Blueprint("Analysis", __name__)


@Analysis.route("/overall", methods=["GET"])
@Auth.auth_required(2)
def overall(session):
    return Helper.render_base_template(session, "analysis/overall.html")


@Analysis.route("/student", methods=["GET"])
@Auth.auth_required(2)
def student(session):
    return Helper.render_base_template(session, "analysis/student.html")


@Analysis.route("/club", methods=["GET"])
@Auth.auth_required(2)
def club(session):
    return Helper.render_base_template(session, "analysis/club.html")


@Analysis.route("/generate-overall", methods=["GET"])
@Auth.auth_required(2)
def download_overall(session):
    file_name = Generator.generate_overall_analysis()

    current_app.logger.info(f"{session} downloaded the overall analysis file")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_OVERALL,
                               attachment_filename=file_name,
                               as_attachment=True)


@Analysis.route("/generate-student", methods=["GET"])
@Auth.auth_required(2)
@Helper.request_args("student-id")
def download_student(session, student_id):
    record = GlobalContext.STUDENTS_DATASTORE.return_specific_entries("UID", student_id)
    if len(record) != 1:
        flash("Invalid student ID, failed to generate the analysis file.")
        return redirect("/student")

    file_name = Generator.generate_student_analysis(student_id)

    current_app.logger.info(f"{session} downloaded the analysis file for a student with the ID {student_id}")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_STUDENT,
                               attachment_filename=file_name,
                               as_attachment=True)


@Analysis.route("/generate-club", methods=["GET"])
@Auth.auth_required(2)
@Helper.request_args("club-id")
def download_club(session, club_id):
    record = GlobalContext.CLUBS_DATASTORE.return_specific_entries("UID", club_id)
    if len(record) != 1:
        flash("Invalid club ID, failed to generate the analysis file.")
        return redirect("/club")

    file_name = Generator.generate_club_analysis(club_id)

    current_app.logger.info(f"{session} downloaded the analysis file for a club with the ID {club_id}")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_CLUB,
                               attachment_filename=file_name,
                               as_attachment=True)
