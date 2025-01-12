import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILENAME = "credit_karma.db"

WEB_DRIVER_PORT = 4446

DESKTOP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36"

PARENT_CREDENTIAL_ACCOUNT = "Credit Karma"
CHILD_CREDENTIAL_ACCOUNTS = ["PayPal", "American Express", "Citi"]

FLASK_HOST = "0.0.0.0"
FLASK_DEFAULT_PORT = 8786
