from .logging_utils import log_function_calls

@log_function_calls
def validate_string_with_regex(string, regex):

    '''function to validate string using regex'''
    import re
    if string is None:
        return False
    return re.match(regex, string) is not None

@log_function_calls
def is_valid_url(string):

    '''
    Function to validate if a string is a url
    https://stackoverflow.com/a/60267538/14741406
    https://urlregex.com/
    '''
    URL = r"(^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$)"
    regex = URL
    return validate_string_with_regex(string, regex)

@log_function_calls
def is_valid_unix_uri(string):

    '''
    Function to validate if a string is a unix url
    Supports common path characters: letters, numbers, underscores, dashes, dots, and spaces.
    '''
    UNIXPATH = r"^(\/[\w\-. ]+)+\/?([\w\-. ])+$"
    regex = UNIXPATH
    return validate_string_with_regex(string, regex)

@log_function_calls
def is_valid_email(string):

    '''
    Function to validate if a string is an email url
    '''
    EMAIL = r"(^(mailto\:)?[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    regex = EMAIL
    return validate_string_with_regex(string, regex)
@log_function_calls
def is_image_url(string):

    '''
    Function to validate if a string is an image url
    '''
    IMAGE_URL = r".*\.(jpg|jpeg|png|gif|bmp|webp|tiff|svg|ico)$"
    regex = IMAGE_URL
    import re
    return re.match(regex, string.lower()) is not None
