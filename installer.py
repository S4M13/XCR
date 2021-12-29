import requests
import shutil
import zipfile
import os
import time
import pathlib
import json

# Settings

CWD = pathlib.Path(os.path.dirname(__file__))

SERVER_URI = "http://extra-curricular-register-server.000webhostapp.com/"
LATEST_VERSION_ENDPOINT = "latest_version"
DOWNLOAD_LATEST_ENDPOINT = "download_latest.php"
AFTER_UPDATE_ENDPOINT = "successful_update.php"
CHECK_IN_ENDPOINT = "check_in.php"

CONFIG_FILE = CWD / "config.json"

UPDATE_CHECK_DELAY = 1 * 60 # * 60

TEMP_DOWNLOAD_FILE = CWD / "download.zip"

CONTENT_FILE = CWD / "app"

# Main Loop

while True:
    try:
        print("[+]Running Cycle")

        # Attempt to fetch product key and version
        with open(CONFIG_FILE, "r") as pkf:
            config = json.load(pkf)
            product_key = config["product_key"]
            version = config["version"]

        # Attempt to fetch the latest version
        latest_version = requests.get(SERVER_URI + LATEST_VERSION_ENDPOINT).content.decode("utf-8")

        # If the latest version is more recent than the current, move to update
        if float(latest_version) != float(version):
            print(f"[+]New update found, updating to version {latest_version}")

            # Stop the software from running
            print("[+]Stopping software")
            os.system("systemctl stop xcr-server")
            time.sleep(5)

            # Download the latest version
            print("[+]Downloading latest version")
            newest_version = requests.get(SERVER_URI + DOWNLOAD_LATEST_ENDPOINT, params={'product_key': product_key})

            # Ensure product key validated properly
            if b"Invalid" in newest_version.content:
                print("[+]Invalid product key - skip update and try again later.")
                continue

            # Save latest version
            print("[+]Installing...")
            with open(TEMP_DOWNLOAD_FILE, "wb") as archive:
                archive.write(newest_version.content)

            # Remove the old version
            shutil.rmtree(CONTENT_FILE)

            # Extract file
            with zipfile.ZipFile(TEMP_DOWNLOAD_FILE, "r") as zip_ref:
                zip_ref.extractall(CWD)

            # Remove the temp file
            print("[+]Clearing up...")
            os.remove(TEMP_DOWNLOAD_FILE)

            # Update the new version
            with open(CONFIG_FILE, "w") as vf:
                config["version"] = latest_version
                json.dump(config, vf)

            # Restart the software
            print("[+]Restarting software")
            os.system("systemctl start xcr-server")
            time.sleep(5)
            print("[+]Update complete")

            print("[+]Checking in with server...")
            req = requests.get(SERVER_URI + AFTER_UPDATE_ENDPOINT,
                               params={"server_name": config["server_name"],
                                       "server_id": config["server_id"],
                                       "current_version": config["version"]})

            if b"Success" in req.content:
                print("[+]Successfully checked in with the server")
            else:
                print("[-]Check in with server failed")
        else:
            print(f"[-]No updated version found - current version {latest_version}. Checking in with server")

            req = requests.get(SERVER_URI + CHECK_IN_ENDPOINT,
                               params={"server_name": config["server_name"],
                                       "server_id": config["server_id"],
                                       "current_version": config["version"]})

            if b"Success" in req.content:
                print("[+]Successfully checked in with the server")
            else:
                print("[-]Check in with server failed")

        time.sleep(UPDATE_CHECK_DELAY)
    except Exception as e:
        print("Failed to check for update: ")
        raise e
