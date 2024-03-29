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
    """
    GET endpoint which returns the overall analysis page.

    :return: The rendered page
    """

    return Helper.render_base_template(session,
                                       "analysis/overall.html",
                                       warning=GlobalContext.DATABASE_ANALYSIS["WARNING"])


@Analysis.route("/student", methods=["GET"])
@Auth.auth_required(2)
def student(session):
    """
    GET endpoint which returns the student analysis page.

    :return: The rendered page
    """

    return Helper.render_base_template(session,
                                       "analysis/student.html",
                                       warning=GlobalContext.DATABASE_ANALYSIS["WARNING"])


@Analysis.route("/club", methods=["GET"])
@Auth.auth_required(2)
def club(session):
    """
    GET endpoint which returns the club analysis page.

    :return: The rendered page
    """

    return Helper.render_base_template(session,
                                       "analysis/club.html",
                                       warning=GlobalContext.DATABASE_ANALYSIS["WARNING"])


@Analysis.route("/generate-overall", methods=["GET"])
@Auth.auth_required(2, page=False)
def download_overall(session):
    """
    GET endpoint which generates and returns an overall analysis Excel file using the generate_overall_analysis function.

    :return: send_file object containing the overall analysis file
    """

    file_name = Generator.generate_overall_analysis()

    current_app.logger.info(f"{session} downloaded the overall analysis file")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_OVERALL,
                               attachment_filename=file_name,
                               as_attachment=True,
                               cache_timeout=0)


@Analysis.route("/generate-student", methods=["GET"])
@Auth.auth_required(2, page=False)
@Helper.request_args("student-id")
@Helper.ensure_valid_student_id(1)
def download_student(session, student_id):
    """
    GET endpoint which generates and returns an student analysis Excel file using the generate_student_analysis function.
    
    :param student_id: The ID code for the associated student
    :return: send_file object containing the analysis file
    """

    file_name = Generator.generate_student_analysis(student_id)

    current_app.logger.info(f"{session} downloaded the analysis file for a student with the ID {student_id}")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_STUDENT,
                               attachment_filename=file_name,
                               as_attachment=True,
                               cache_timeout=0)


@Analysis.route("/generate-club", methods=["GET"])
@Auth.auth_required(2, page=False)
@Helper.request_args("club-id")
@Helper.ensure_valid_club_id(1)
def download_club(session, club_id):
    """
    GET endpoint which generates and returns an club analysis Excel file using the generate_club_analysis function.
    
    :param club_id: The ID code for the associated club
    :return: send_file object containing the analysis file
    """

    file_name = Generator.generate_club_analysis(club_id)

    current_app.logger.info(f"{session} downloaded the analysis file for a club with the ID {club_id}")

    return send_from_directory(Settings.EXPORTS,
                               Settings.CURRENT_CLUB,
                               attachment_filename=file_name,
                               as_attachment=True,
                               cache_timeout=0)
