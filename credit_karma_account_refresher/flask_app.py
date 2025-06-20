import pathlib
from pprint import pprint
import re
import socket
import threading

from flask import Flask, request

from constants import SCRIPT_DIR, FLASK_HOST, FLASK_DEFAULT_PORT, PARENT_CREDENTIAL_ACCOUNT
from globals import (
    current_otp_dict_list,
    credentials_dict_list,
    flask_port_mapping_dict,
)
from otp import update_otp


def run_flask_app():
    app = Flask(__name__)

    @app.route("/sms", methods=["POST"])
    def receive_sms():
        global current_otp_dict_list, credentials_dict_list

        print("SMS received")

        data = request.json

        print("JSON response:")
        pprint(data)

        message = data.get("message")
        if not message:
            message = data.get("msg")

        _time = data.get("time")
        filter_name = data.get("filter-name")
        in_number = data.get("in-number")
        in_sim = data.get("in-sim")

        print(f"SMS message: {message}")
        print(f"SMS time: {_time}")
        print(f"SMS filter-name: {filter_name}")
        print(f"SMS in-number: {in_number}")
        print(f"SMS in-sim: {in_sim}")

        account = ""
        otp_code = ""
        if "credit karma" in filter_name.lower():
            account = "Credit Karma"
            otp_code = re.search("Code: (......)", message).group(1)
        elif "paypal" in filter_name.lower():
            account = "PayPal"

            match = re.search(
                "PayPal: (......) is your code", message
            )

            if not match:
                # old message but may come back some day
                match = re.search(
                    "PayPal: (......) is your security code", message
                )

            if not match:
                # fallback
                match = re.search(
                    "PayPal: (......)", message
                )

            otp_code = match.group(1)
        else:
            raise Exception(f"Unkown account filter: {filter_name}")

        if any([not c.isdigit() for c in otp_code]):
            raise Exception(f"OTP is not all digits: {otp_code}")

        username = ""

        # get username from filter name and credentials config
        for parent_credentials_dict in credentials_dict_list:
            if account.lower().strip() == PARENT_CREDENTIAL_ACCOUNT.lower().strip():
                if (
                    not parent_credentials_dict["account"].lower().strip()
                    == account.lower().strip()
                ):
                    continue

                if parent_credentials_dict["username"].lower().strip() in filter_name.lower():
                    username = parent_credentials_dict["username"]
                    break
            else:
                if "child_accounts" in parent_credentials_dict:
                    for child_credentials_dict in parent_credentials_dict["child_accounts"]:
                        if (
                            not child_credentials_dict["account"].lower().strip()
                            == account.lower().strip()
                        ):
                            continue

                        if child_credentials_dict["username"].lower().strip() in filter_name.lower():
                            username = child_credentials_dict["username"]
                            break

        if not username:
            raise Exception(
                f"Unable to find username in this filter: {filter_name.lower()}"
            )

        update_otp(account, username, otp_code)

        print(f"Set OTP for account {account} and username {username} to {otp_code}")

        # print("Current OTP dict:")
        # pprint(current_otp_dict_list)

        return "Received", 200

    port = FLASK_DEFAULT_PORT

    actual_hostname = socket.gethostname()

    found_port_mapping = False
    for hostname_key in flask_port_mapping_dict:
        if actual_hostname.lower().strip() == hostname_key.lower().strip():
            port = int(flask_port_mapping_dict[hostname_key])
            print(f"Running on hostname {actual_hostname}, so using port {port}")
            found_port_mapping = True
            break

    if not found_port_mapping:
        print(f"Running on port {port}")

    app.run(
        host=FLASK_HOST,
        port=port,
        ssl_context=(
            str(pathlib.Path(SCRIPT_DIR) / "keys" / "fullchain.pem"),
            str(pathlib.Path(SCRIPT_DIR) / "keys" / "privkey.pem"),
        ),
    )


def start_flask_thread():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = (
        True  # allow the program to exit even if the Flask thread is running
    )
    flask_thread.start()
