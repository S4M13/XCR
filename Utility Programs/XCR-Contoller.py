#This program pushes the update to the server

from ftplib import FTP
import requests
import zipfile
import pathlib
import os
import string
import random

# Helper Functions
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def connect_to_ftp(debug=False):
	print("[-]Connecting to the FTP server")
	ftp = FTP(FTP_HOST)
	if debug:
		ftp.set_debuglevel(1)
	ftp.login(FTP_USER, FTP_PASS)
	print("[+]Successfully connected")

	return ftp

def generate_license():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(20))
    return result_str

#Settings

SERVER_URI = "http://extra-curricular-register-server.000webhostapp.com/"
LATEST_VERSION_ENDPOINT = "latest_version"

LATEST_VERSION_NAME = "current_version.zip"

FTP_HOST = "files.000webhost.com"
FTP_USER = "extra-curricular-register-server"
FTP_PASS = "C8mOlUi)H^HLsWAkfbfQ"

DEVELOPMENT_VERSION_PATH = pathlib.Path("app/")

PRODUCT_KEY_FILE = "valid_product_keys.txt"

#Option Functions

def upload_new_version():
	# Log into the FTP server
	ftp = connect_to_ftp()

	# Get the new version number
	VERSION_NUMBER = input("Version Number: ")

	# Create a temp file containing this number
	print("[+]Creating the temporary version file")
	with open(LATEST_VERSION_ENDPOINT, "w") as file:
	 	file.write(VERSION_NUMBER)

	# Package the development version and ship it
	os.chdir("DevelopmentEnv")
	print("[+]Packaging the latest version into a archive")
	zipf = zipfile.ZipFile(LATEST_VERSION_NAME, 'w', zipfile.ZIP_DEFLATED)
	zipdir(DEVELOPMENT_VERSION_PATH, zipf)
	zipf.close()
	os.chdir("..")

	#Upload the files overwriting current files
	print("[-]Uploading the new files...")
	with open("DevelopmentEnv/" + LATEST_VERSION_NAME, "rb") as uploading:
		ftp.storbinary("STOR " + LATEST_VERSION_NAME, uploading)

	ftp.cwd("public_html/")

	with open(LATEST_VERSION_ENDPOINT, "rb") as uploading:
		ftp.storbinary("STOR " + LATEST_VERSION_ENDPOINT, uploading)

	print("[+]Successfully uploaded the new files to the server")

	#Close the connection
	print("[+]Closing the FTP connection")
	ftp.quit()
	ftp.close()

	#Remove temp files
	print("[+]Removing temp files")
	os.remove("DevelopmentEnv/" + LATEST_VERSION_NAME)
	os.remove(LATEST_VERSION_ENDPOINT)

	#Checking the server
	print("[-]Running checks to ensure upload is successfull...")
	latest_version = requests.get(SERVER_URI + LATEST_VERSION_ENDPOINT).content.decode("utf-8")

	if latest_version == VERSION_NUMBER:
		print("[+]Verified successfull upload")
	else:
		print("[-]Verification failed, please manually review")


def add_new_license():
	#Connect to FTP
	ftp = connect_to_ftp()

	#Get a new license
	NEW_LICENSE = input("Please enter a valid license [Leave blank to generate] > ") or generate_license()
	print("[+]Registering license key: " + NEW_LICENSE)

	#Download current license file
	with open(PRODUCT_KEY_FILE, "wb") as pkf:
		ftp.retrbinary("RETR " + PRODUCT_KEY_FILE, pkf.write)

	#Append the new key

	with open(PRODUCT_KEY_FILE, "r") as pkf:
		current = pkf.readlines()

	with open(PRODUCT_KEY_FILE, "w") as pkf:
		try:
			current.remove("\n")
		except ValueError:
			pass

		current.append(NEW_LICENSE + "\n")
		print(current)
		pkf.write("".join(current))


	with open(PRODUCT_KEY_FILE, "rb") as pkf:
		ftp.storlines("STOR " + PRODUCT_KEY_FILE, pkf)


	print("[+]Registered new license key")

	print("[+]Removing temp files")
	os.remove(PRODUCT_KEY_FILE)

	#Close the connection
	print("[+]Closing the FTP connection")
	ftp.quit()
	ftp.close()


#Start main menu

while True:
	print("[-]XCR Main Menu Control[-]\n")
	print("Please select what you would like to do: ")
	print("    1. Check the active logs")
	print("    2. Upload a new version")
	print("    3. Register a new valid license\n")

	print("    Type exit to exit\n")

	answer = "a"

	while answer not in "123" and answer != "exit":
		answer = input("> ")

	if answer == "1":
		pass
	if answer == "2":
		print("\n" + "="*20 + "Uploading a new version" + "="*20)
		upload_new_version()
		print("="*20 + "Uploaded a new version" + "="*20)
		print("\n"*2)
	if answer == "3":
		print("\n" + "="*20 + "Adding a new license" + "="*20)
		add_new_license()
		print("="*20 + "Added a new license" + "="*20)
		print("\n"*2)

	if answer == "exit":
		break
