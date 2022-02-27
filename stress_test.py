from __future__ import print_function
from locust import Locust, TaskSet, task, HttpLocust, between, HttpUser, tag
import json
import greenlet


class UserBehavior(HttpUser):

	def __init__(self, parent):
		super(UserBehavior, self).__init__(parent)

		self.token = None
		self.jar = None

	def on_start(self):
		self.client.verify = False

		self.login()

	def login(self):
		response = self.client.post("/auth", data={'username':'admin', 'password':'admin'}, allow_redirects=False)

		if response.status_code == 302:
			self.jar = response.cookies

		self.ensureLoggedIn()

	def ensureLoggedIn(self):
		with self.client.get("/", cookies=self.jar, catch_response=True, allow_redirects=False) as response:
			if response.status_code == 302:
				response.failure("Not successfully logged in")

	# Browsing behaviour

	@tag('browse')
	@task(1)
	def home(self):
		self.client.get("/", cookies=self.jar)

	@tag('browse')
	@task(1)
	def register_class(self):
		self.client.get("/register_class", cookies=self.jar)

	@tag('browse')
	@task(1)
	def register_individual(self):
		self.client.get("/register_one", cookies=self.jar)

	@tag('browse')
	@task(1)
	def view_records(self):
		self.client.get("/view_records", cookies=self.jar)

	@tag('browse')
	@task(1)
	def overall(self):
		self.client.get("/overall", cookies=self.jar)

	@tag('browse')
	@task(1)
	def student(self):
		self.client.get("/student", cookies=self.jar)

	@tag('browse')
	@task(1)
	def club(self):
		self.client.get("/club", cookies=self.jar)

	@tag('browse')
	@task(1)
	def users(self):
		self.client.get("/users", cookies=self.jar)

	@tag('browse')
	@task(1)
	def sessions(self):
		self.client.get("/sessions", cookies=self.jar)

	@tag('browse')
	@task(1)
	def data(self):
		self.client.get("/data", cookies=self.jar)

	@tag('browse')
	@task(1)
	def logs(self):
		self.client.get("/logs", cookies=self.jar)

	wait_time = between(1, 5)
