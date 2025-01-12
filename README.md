# Description
Automatically refreshes all your Credit Karma linked accounts every ~12 hours. Credit Karma itself does not
keep all accounts refreshed when you actually need to check your balances and transactions history. This
ensures you'll always see up-to-date account info.

# Setup
Install SMS Forwarder on the smartphone that receives SMS OTP codes. Create filter that matches Credit Karma
keywords. Name the filter Credit Karma and also include your Credit Karma username (email). This is needed
to support multiple accounts and will match to the correct account. Make the SMS Forwarder filter do a POST
to the IP or domain name on port 8786 by default. A Flask server thread is created on startup that listens
for these SMS forwards and sets global variables containing the OTPs found.

# Security
Passwords are stored using keyring. For Windows, they are stored in the Windows Credential Manager.
Only usernames and other non-sensitive info is stored in config files.

# Current Restrictions
For actual linked accounts, currently only PayPal OTP via SMS is supported. If a linked account requires credentials,
it will be skipped for now until this is implemented.
