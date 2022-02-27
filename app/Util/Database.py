from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
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
    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    student_uid = db.Column(db.Integer, nullable=False)
    club_uid = db.Column(db.Integer, nullable=False)
    attendance_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Record entry [{self.student_uid}:{self.club_uid}:{self.attendance_date}]>"


class Preset(db.Model):
    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    entries = db.relationship('PresetEntry', backref='preset', lazy=True)

    def __repr__(self):
        return f"<Preset [{self.id}:{self.name}]>"


class PresetEntry(db.Model):
    __bind_key__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    student_uid = db.Column(db.Integer, nullable=False)
    preset_id = db.Column(db.Integer, db.ForeignKey('preset.id'), nullable=False)

    def __repr__(self):
        return f"<Preset Entry [{self.id}:{self.student_uid}:{self.preset.name}]>"
