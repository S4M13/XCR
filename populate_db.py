import sqlite3
import random
import datetime
from functools import wraps

DATABASE = "C:\\Users\\samdo\\Desktop\\final\\app\\Data\\Database\\Records.db"
MAX_STUDENT_UID = 900
MAX_CLUB_UID = 20

ATTENDED_ANY_CLUB_CHANCE = 0.7
ATTENDANCE_CHANCE_START_RANGE = 0.2
ATTENDANCE_CHANCE_END_RANGE = 0.9

ATTENDANCE_OPPERTUNITIES = 35


connection = sqlite3.connect(DATABASE)

def insert_record(c, student_uid: int, club_uid: int, date: datetime.datetime):
	c.execute("INSERT INTO record VALUES(NULL, ?, ?, ?);", (int(student_uid), int(club_uid), date))

def chance(chance: float):
	return random.uniform(0.1, 1) < chance

def random_club_uid():
	return random.randint(1, MAX_CLUB_UID)



def populate():


	for student_uid in range(1, MAX_STUDENT_UID+1):
		print(student_uid)
		if chance(ATTENDED_ANY_CLUB_CHANCE):
			cursor = connection.cursor()
			
			#Pick a random club and then add attendance records dependant of attendance chance
			club_uid = random_club_uid()
			attendance_rate = random.uniform(ATTENDANCE_CHANCE_START_RANGE, ATTENDANCE_CHANCE_END_RANGE)

			start_date = datetime.date(2020, 1, 1)
			end_date = datetime.date(2020, 2, 1)

			time_between_dates = end_date - start_date
			days_between_dates = time_between_dates.days
			random_number_of_days = random.randrange(days_between_dates)

			random_date = start_date + datetime.timedelta(days=random_number_of_days)

			current_date = random_date

			for i in range(ATTENDANCE_OPPERTUNITIES):
				if chance(attendance_rate):
					insert_record(cursor, student_uid, club_uid, current_date)

				current_date = current_date + datetime.timedelta(days=7)

			connection.commit()
			cursor.close()


def fix():
	cursor = connection.cursor()

	cursor.execute("SELECT * FROM record;")

	data = cursor.fetchall()

	for entry in data:
		if "00:00:00.000000" not in entry[3]:
			cursor.execute("UPDATE record SET attendance_date = ? WHERE id = ?;", (entry[3] + " 00:00:00.000000", int(entry[0])))

	connection.commit()
	cursor.close()


fix()
connection.close()




