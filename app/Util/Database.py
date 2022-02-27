from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """
    USER database model - models users: entities which may log into the application.

    :param id: The ID of the user (Unique, Primary Key)
    :param name: The name of the user
    :param password_hash: The hash of the user's password
    :param auth_level: The authentication level that the users should have access to.
    """

    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    auth_level = db.Column(db.Integer, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256:80000")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User entry [{self.name}:{self.id}]>"


class Record(db.Model):
    """
    RECORDS database model - models records: entities store records of attendance for a student, time and club.

    :param id: The ID of the records (Unique, Primary Key)
    :param student_uid: The ID of the student (Foreign Key)
    :param club_uid: The ID of the club (Foreign Key)
    :param attendance_date: The timestamp of the attendance for the record.
    """

    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    student_uid = db.Column(db.Integer, nullable=False)
    club_uid = db.Column(db.Integer, nullable=False)
    attendance_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Record entry [{self.student_uid}:{self.club_uid}:{self.attendance_date}]>"


class Preset(db.Model):
    """
    PRESET database model - models presets: entities store preset registers users can load - currently being added on
    end clients recommendation.

    :param id: The ID of the records (Unique, Primary Key)
    :param name: The name of the preset
    """

    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    entries = db.relationship('PresetEntry', backref='preset', lazy=True)

    def __repr__(self):
        return f"<Preset [{self.id}:{self.name}]>"


class PresetEntry(db.Model):
    """
    PRESET_ENTRY database model - models preset entries: entities which record the students stored in a preset -
    currently being added on end clients recommendation.

    :param id: The ID of the records (Unique, Primary Key)
    :param student_uid: The ID of the associated student
    :param preset_id: The ID of the associated preset (Foreign Key)
    """

    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    student_uid = db.Column(db.Integer, nullable=False)
    preset_id = db.Column(db.Integer, db.ForeignKey('preset.id'), nullable=False)

    def __repr__(self):
        return f"<Preset Entry [{self.id}:{self.student_uid}:{self.preset.name}]>"
