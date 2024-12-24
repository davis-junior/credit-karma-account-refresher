import json
import pathlib
from pprint import pprint
import traceback


def make_and_get_directory_path():
    directory_path = pathlib.Path("ckar_config")
    directory_path.mkdir(exist_ok=True, parents=True)
    return directory_path


def get_flask_port_mapping_file_path():
    directory_path = make_and_get_directory_path()
    return directory_path / "flask_port_mapping.json"


def save_flask_port_mappings(flask_port_mapping_dict: dict):
    """Does not utilize global var"""

    file_path = get_flask_port_mapping_file_path()

    with open(str(file_path), "w", encoding="utf-8") as f:
        json.dump(flask_port_mapping_dict, f, indent=4)


def load_flask_port_mappings() -> dict:
    """Does not utilize global var"""

    file_path = get_flask_port_mapping_file_path()
    if not file_path.exists():
        return {}

    flask_port_mapping_dict = {}

    try:
        with open(str(file_path), "r", encoding="utf-8") as f:
            flask_port_mapping_dict = json.load(f)
    except:
        traceback.print_exc()

    return flask_port_mapping_dict


def main():
    global flask_port_mapping_dict
    from globals import flask_port_mapping_dict

    print("Current flask port mappings:")
    pprint(flask_port_mapping_dict)

    to_delete_list = []

    # only ask to update/delete existing mappings once
    for hostname in flask_port_mapping_dict:
        update = input(
            f"Would you like to update hostname {hostname} port {flask_port_mapping_dict[hostname]}? (Y or N): "
        )
        update = update.strip().upper()
        if update == "Y":
            port = input(f"Enter port for {hostname}: ")
            flask_port_mapping_dict[hostname] = int(port.strip())
            continue

        delete = input(
            f"Would you like to delete hostname {hostname} port {flask_port_mapping_dict[hostname]}? (Y or N): "
        )
        delete = delete.strip().upper()
        if delete == "Y":
            to_delete_list.append(hostname)
            continue

    for hostname in to_delete_list:
        del flask_port_mapping_dict[hostname]

    while True:
        add = input("Would you like to add a new hostname to port mapping? (Y or N): ")
        add = add.strip().upper()
        if add == "Y":
            hostname = input(f"Enter hostname: ").strip()
            port = input(f"Enter port for {hostname}: ")
            flask_port_mapping_dict[hostname] = int(port.strip())
        else:
            break

    print("Current flask port mappings:")
    pprint(flask_port_mapping_dict)

    save_flask_port_mappings(flask_port_mapping_dict)


if __name__ == "__main__":
    main()
