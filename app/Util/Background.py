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
    """
    This function refreshes the database statistics every 60 seconds in the background constantly updating the cache.
    Hence this prevents users having to wait the initial delay while the cache is updated in case it is invalidated and
    hence leads to an increase in performance.
    """

    with scheduler.app.app_context():
        Helper.update_database_analysis()
        current_app.logger.debug("Database successfully refreshed")









