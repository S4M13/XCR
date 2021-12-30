from flask import Flask
from flask_apscheduler import APScheduler
from flask import current_app

if __name__ == "__main__":
    import GlobalContext
    import Helper
else:
    from Util import GlobalContext
    from Util import Helper

scheduler = APScheduler()


@scheduler.task('interval', id='db_refresh', seconds=60, misfire_grace_time=900)
def db_refresh():
    with scheduler.app.app_context():
        Helper.update_database_analysis()
        current_app.logger.info("Database successfully refreshed")









