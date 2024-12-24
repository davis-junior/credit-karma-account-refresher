from globals import current_otp_dict_list


def _get_otp_dict(account: str, username: str):
    global current_otp_dict_list

    account = _get_uniform_account(account)

    for otp_dict in current_otp_dict_list:
        if (
            otp_dict.get("account").lower().strip() == account.lower().strip()
            and otp_dict.get("username").lower().strip() == username.lower().strip()
        ):
            return otp_dict

    return {}


def _get_uniform_account(account: str):
    account = account.lower().strip()

    if "credit karma" in account:
        return "credit karma"
    elif "paypal" in account:
        return "paypal"

    return account


def get_otp(account: str, username: str):
    account = _get_uniform_account(account)

    return _get_otp_dict(account, username).get("otp")


def update_otp(account: str, username: str, otp: str):
    global current_otp_dict_list

    account = _get_uniform_account(account)

    otp_dict = _get_otp_dict(account, username)

    if otp_dict:
        # since there is already a dict, update instead of adding new
        otp_dict["otp"] = otp
    else:
        # since there is no existing dict, add new
        current_otp_dict_list.append(
            {
                "account": account,
                "username": username,
                "otp": otp,
            }
        )
