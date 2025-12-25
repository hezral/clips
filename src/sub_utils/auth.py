import keyring
from .logging_utils import log_function_calls


@log_function_calls
def do_authentication(action, password=None):


    def set_password(password):
        try:
            return True, keyring.set_password("com.github.hezral.clips", "clips", password)
        except:
            return False, keyring.errors

    def get_password():
        try:
            return True, keyring.get_password("com.github.hezral.clips", "clips")
        except:
            return False, keyring.errors

    if action == "get":
        return get_password()
    elif action == "set":
        return set_password(password)
    elif action == "reset":
        return get_password(), set_password(password)
