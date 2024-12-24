import getpass
import json
import keyring
import pathlib
from pprint import pprint
import traceback

from constants import CREDENTIALS_ACCOUNTS


def get_password(account_name: str, username: str):
    return keyring.get_password(
        f"ckar-{account_name.lower().replace(' ', '_')}", username.strip()
    )


def set_password(account_name: str, username: str, password: str):
    keyring.set_password(
        f"ckar-{account_name.lower().replace(' ', '_')}", username.strip(), password
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


def get_credentials_dict(account: str, username: str):
    global credentials_dict_list
    from globals import credentials_dict_list

    for d in credentials_dict_list:
        if (
            d["account"].lower().strip() == account.lower().strip()
            and d["username"].lower().strip() == username.lower().strip()
        ):
            return d


def main():
    global credentials_dict_list
    from globals import credentials_dict_list

    print("Current credentials:")
    pprint(credentials_dict_list)

    while True:
        for account in CREDENTIALS_ACCOUNTS:
            add = input(f"Would you like to add credentials for {account}? (Y or N): ")
            add = add.strip().upper()
            if add == "N":
                continue

            username = input(f"Enter username for {account}: ")

            # check if username already in credentials_dict_list and ask if want to update password
            credentials_dict = get_credentials_dict(account, username)
            if credentials_dict:
                print(f"Account {account} for username {username} already exists")
                add = input("Do you want to update the password? (Y or N): ")
                add = add.strip().upper()
                if add == "N":
                    continue

            password = getpass.getpass(f"Enter password for {account}: ")
            set_password(account, username, password)

            if not credentials_dict:
                # add username and account to credentials_dict_list
                credentials_dict_list.append(
                    {
                        "account": account,
                        "username": username,
                    }
                )

        add_another = input("Would you like to add another account? (Y or N): ")
        add_another = add_another.strip().upper()
        if add_another == "N":
            break

    print("Current credentials:")
    pprint(credentials_dict_list)

    save_accounts_and_usernames(credentials_dict_list)


if __name__ == "__main__":
    main()
