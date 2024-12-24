import random
import sqlite3
import time
import traceback

from automation import refresh_accounts
from cli import get_input_with_timeout
from constants import DB_FILENAME
from credentials import get_password
from credentials import main as credentials_main
from db import create_tables
from driver import get_new_driver
from flask_app import start_flask_thread
from flask_port_mapping import main as flask_port_mapping_main
from globals import credentials_dict_list


def refresh_all_accounts(cursor: sqlite3.Cursor):
    for credentials_dict in credentials_dict_list:
        # only get Credit Karma accounts
        if credentials_dict["account"].lower().strip() != "credit karma":
            continue

        try:
            driver = get_new_driver()

            refresh_accounts(
                driver,
                cursor,
                credentials_dict["username"],
                get_password(credentials_dict["account"], credentials_dict["username"]),
            )
            print(
                f"Successfully refreshed Credit Karma accounts for username {credentials_dict['username']}"
            )
        except:
            traceback.print_exc()
            print(
                f"Error detected for Credit Karma username {credentials_dict['username']}. Trying again in about an hour..."
            )

            time.sleep(3600 + random.randint(180, 900))
            continue
        finally:
            time.sleep(2)
            print("Quitting driver...")
            driver.quit()

        print("Waiting about 15 minutes...")
        time.sleep(900 + random.randint(120, 220))


def credit_karma_credentials_exist() -> bool:
    global credentials_dict_list

    if credentials_dict_list:
        # make sure at least one Credit Karma account is in credentials global
        for credentials_dict in credentials_dict_list:
            if credentials_dict["account"].lower().strip() == "credit karma":
                return True

    return False


def main():
    response = get_input_with_timeout(
        "Do you want to make a config change? (Y/N): ", 15
    )

    if response and response.upper().strip() == "Y":
        credentials_main()
        flask_port_mapping_main()

    start_flask_thread()

    if not credit_karma_credentials_exist():
        print("No Credit Karma credentials found. Requesting credentials now...")
        credentials_main()

    # check one more time and exit if no credentials
    if not credit_karma_credentials_exist():
        print("No Credit Karma credentials found still. Exiting program...")
        return

    while True:
        try:
            with sqlite3.connect(DB_FILENAME, isolation_level=None) as conn:
                cursor = conn.cursor()

                create_tables(cursor)

                refresh_all_accounts(cursor)
        except:
            traceback.print_exc()

        print("Waiting about 8-9 hours...")
        time.sleep(28800 + random.randint(900, 3600))


if __name__ == "__main__":
    main()
