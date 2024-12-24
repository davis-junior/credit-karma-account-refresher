from credentials import load_accounts_and_usernames
from flask_port_mapping import load_flask_port_mappings


credentials_dict_list = load_accounts_and_usernames()
current_otp_dict_list = []
flask_port_mapping_dict = load_flask_port_mappings()
