import pathlib
import os

# Settings.py
CURRENT_VERSION = "Alpha-7.9"

CWD = pathlib.Path(os.path.dirname(__file__))

SERVER_CONFIG = CWD / ".." / "config.json"

LOG_FILE_LOCATION = CWD / "Logs" / "last_run.log"
LOG_FILE_DIRECTORY = CWD / "Logs"

CERTFILE_LOCATION = CWD / ".." / "Keys" / "ca.crt"
KEYFILE_LOCATION = CWD / ".." / "Keys" / "private.key"

DATABASE_LOCATION = CWD / "Data" / "Database"
USER_DATABASE_NAME = "Users.db"
RECORDS_DATABASE_NAME = "Records.db"

RECORD_DATABASE_BIND = "sqlite:///" + str(DATABASE_LOCATION / RECORDS_DATABASE_NAME)
USER_DATABASE_BIND = "sqlite:///" + str(DATABASE_LOCATION / USER_DATABASE_NAME)

MAX_LOGIN_ATTEMPTS = 5
MAX_LOGIN_ATTEMPT_PERIOD = 1 * 60

SESSION_COOKIE_NAME = "session_id"
SESSION_TIMEOUT = 1 * 60 * 30

COOKIE_SAME_SITE = 'Lax'  # TODO: Change to secure for production
COOKIE_SECURE = False  # TODO: Change to true for production

PERMISSION_NAMES = {
    0: "Anonymous",
    1: "User",
    2: "Analyst",
    3: "Admin"
}

STUDENT_DATASTORE_LOCATION = CWD / "Data" / "Datastore" / "Students"
CLUBS_DATASTORE_LOCATION = CWD / "Data" / "Datastore" / "Clubs"

DATABASE_ANALYSIS_REFRESH_RATE = 60 * 3

EXPORTS = CWD / "Export"

SPREADSHEETS = CWD / "Spreadsheets"
OVERALL_ANALYSIS_SPREADSHEET = "OverallBase.xlsx"

CURRENT_OVERALL = "OverallAnalysisCurrent.xlsx"
CURRENT_STUDENT = "StudentAnalysisCurrent.xlsx"
CURRENT_CLUB = "ClubAnalysisCurrent.xlsx"
