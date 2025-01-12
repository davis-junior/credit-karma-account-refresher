import getpass
import json
import keyring
import pathlib
from pprint import pprint
import traceback

from constants import PARENT_CREDENTIAL_ACCOUNT, CHILD_CREDENTIAL_ACCOUNTS


def get_child_username(
    parent_account_name: str, parent_username: str, child_account_name: str
):
    global credentials_dict_list
    from globals import credentials_dict_list

    for d in credentials_dict_list:

        if (
            d["account"].lower().strip() == parent_account_name.lower().strip()
            and d["username"].lower().strip() == parent_username.lower().strip()
        ):

            if "child_accounts" in d:
                for child_d in d["child_accounts"]:
                    if (
                        child_d["account"].lower().strip()
                        == child_account_name.lower().strip()
                    ):
                        return child_d["username"]


def get_password(
    parent_account_name: str,
    parent_username: str,
    child_account_name: str = None,
    child_username: str = None,
):

    if not child_account_name or not child_username:
        return keyring.get_password(
            f"ckar-{parent_account_name.lower().replace(' ', '_')}",
            parent_username.strip(),
        )
    else:
        return keyring.get_password(
            f"ckar-{parent_account_name.lower().replace(' ', '_')}-{child_account_name.lower().replace(' ', '_')}",
            f"{parent_username.strip()}-{child_username.strip()}",
        )


def set_password(
    password: str,
    parent_account_name: str,
    parent_username: str,
    child_account_name: str = None,
    child_username: str = None,
):
    if not child_account_name or not child_username:
        keyring.set_password(
            f"ckar-{parent_account_name.lower().replace(' ', '_')}",
            parent_username.strip(),
            password,
        )
    else:
        keyring.set_password(
            f"ckar-{parent_account_name.lower().replace(' ', '_')}-{child_account_name.lower().replace(' ', '_')}",
            f"{parent_username.strip()}-{child_username.strip()}",
            password,
        )


def make_and_get_directory_path():
    directory_path = pathlib.Path("ckar_config")
    directory_path.mkdir(exist_ok=True, parents=True)
    return directory_path


def get_credentials_file_path():
    directory_path = make_and_get_directory_path()
    return directory_path / "credentials.json"


def save_accounts_and_usernames(credentials_dict_list: list):
    """Does not utilize global var"""

    file_path = get_credentials_file_path()

    with open(str(file_path), "w", encoding="utf-8") as f:
        json.dump(credentials_dict_list, f, indent=4)


def load_accounts_and_usernames() -> list[dict]:
    """Does not utilize global var"""

    file_path = get_credentials_file_path()
    if not file_path.exists():
        return []

    credentials_dict_list = []

    try:
        with open(str(file_path), "r", encoding="utf-8") as f:
            credentials_dict_list = json.load(f)
    except:
        traceback.print_exc()

    return credentials_dict_list


def get_credentials_dict(
    parent_account: str,
    parent_username: str,
    child_account: str = None,
    child_username: str = None,
):
    global credentials_dict_list
    from globals import credentials_dict_list

    for d in credentials_dict_list:

        if (
            d["account"].lower().strip() == parent_account.lower().strip()
            and d["username"].lower().strip() == parent_username.lower().strip()
        ):
            if not child_account:
                return d
            else:
                if "child_accounts" in d:
                    for child_d in d["child_accounts"]:
                        if (
                            child_d["account"].lower().strip()
                            == child_account.lower().strip()
                            and child_d["username"].lower().strip()
                            == child_username.lower().strip()
                        ):
                            return d


def handle_parent_account_additions_loop():
    global credentials_dict_list
    from globals import credentials_dict_list

    while True:
        add = input(
            f"Would you like to add parent credentials for {PARENT_CREDENTIAL_ACCOUNT}? (Y or N): "
        )
        add = add.strip().upper()
        if add == "N":
            break

        username = input(f"Enter username for {PARENT_CREDENTIAL_ACCOUNT}: ")

        # check if username already in credentials_dict_list and ask if want to update password
        credentials_dict = get_credentials_dict(PARENT_CREDENTIAL_ACCOUNT, username)
        if credentials_dict:
            print(
                f"Account {PARENT_CREDENTIAL_ACCOUNT} for username {username} already exists"
            )
            add = input("Do you want to update the password? (Y or N): ")
            add = add.strip().upper()
            if add == "N":
                continue

        password = getpass.getpass(
            f"Enter password for {PARENT_CREDENTIAL_ACCOUNT} for user {username}: "
        )
        set_password(password, PARENT_CREDENTIAL_ACCOUNT, username)

        if not credentials_dict:
            # add username and account to credentials_dict_list
            credentials_dict_list.append(
                {
                    "account": PARENT_CREDENTIAL_ACCOUNT,
                    "username": username,
                }
            )

        add_another = input("Would you like to add another parent account? (Y or N): ")
        add_another = add_another.strip().upper()
        if add_another == "N":
            break


def handle_child_account_addition_loop():
    global credentials_dict_list
    from globals import credentials_dict_list

    while True:
        # handle child credentials for each parent
        for parent_account_dict in [
            d
            for d in credentials_dict_list
            if d["account"].lower().strip() == PARENT_CREDENTIAL_ACCOUNT.lower().strip()
        ]:
            parent_account = parent_account_dict["account"]
            parent_username = parent_account_dict["username"]

            for child_account in CHILD_CREDENTIAL_ACCOUNTS:
                add = input(
                    f"Would you like to add child credentials for {child_account} under parent {parent_username}? (Y or N): "
                )
                add = add.strip().upper()
                if add == "N":
                    continue

                username = input(
                    f"Enter username for {child_account} under parent {parent_username}: "
                )

                # check if username already in credentials_dict_list and ask if want to update password
                credentials_dict = get_credentials_dict(
                    parent_account, parent_username, child_account, username
                )
                if credentials_dict:
                    print(
                        f"Account {child_account} for username {username} under parent {parent_username} already exists"
                    )
                    add = input("Do you want to update the password? (Y or N): ")
                    add = add.strip().upper()
                    if add == "N":
                        continue

                password = getpass.getpass(
                    f"Enter password for {child_account} under parent {parent_username}: "
                )
                set_password(
                    password, parent_account, parent_username, child_account, username
                )

                if not credentials_dict:
                    if "child_accounts" not in parent_account_dict:
                        parent_account_dict["child_accounts"] = []

                    # add username and account to credentials_dict_list
                    parent_account_dict["child_accounts"].append(
                        {
                            "account": child_account,
                            "username": username,
                        }
                    )

        add_another = input("Would you like to add another child account? (Y or N): ")
        add_another = add_another.strip().upper()
        if add_another == "N":
            break


def main():
    global credentials_dict_list
    from globals import credentials_dict_list

    print("Current credentials:")
    pprint(credentials_dict_list)

    handle_parent_account_additions_loop()
    handle_child_account_addition_loop()

    print("Current credentials:")
    pprint(credentials_dict_list)

    save_accounts_and_usernames(credentials_dict_list)


if __name__ == "__main__":
    main()
