"""
Global context file - stores a number of variables which are synced across the application and throughout classes.

Ideally would be run from a manager or REDIS/memcached style storage however for a relatively simple single threaded
application such as this that would be slightly excessive.
"""


CONFIG = {}
SERVER_NAME = ""

STUDENTS_DATASTORE = None
CLUBS_DATASTORE = None

DATABASE_ANALYSIS = {}

LOGIN_ATTEMPTS = {}
