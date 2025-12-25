
#-------------------------------------------------------------------------------------------------------
# https://www.blog.pythonlibrary.org/2016/06/09/python-how-to-create-an-exception-logging-decorator/

def init_logger(id, logfile=None):
    """
    Creates a logging object and returns it
    """
    import sys
    import logging
    
    logger = logging.getLogger(id)
    logger.setLevel(logging.NOTSET)
    
    # format_str = "%(levelname)s: %(asctime)s %(pathname)s, %(funcName)s:%(lineno)d: %(message)s"
    format_str = "%(levelname)s: %(asctime)s %(message)s"
    formatter = logging.Formatter(format_str)

    if logfile:
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter) 
    logger.addHandler(stream_handler)

    return logger

# def exception_logger(logger):
#     """
#     A decorator that wraps the passed in function and logs exceptions should one occur
#     
#     @param logger: a logging object
#     """
#     
#     def decorator(func):
#     
#         def wrapper(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except:
#                 err = "There was an exception in  "
#                 err += func.__name__
#                 logger.exception(err)
#             
#             # re-raise the exception
#             raise
#         return wrapper
#     return decorator

def log_function_calls(func):
    """
    A decorator that logs the entry and exit of a function, including its arguments and return value.
    Attempts to find a logger from `self.logger`, `self.app.logger`, or falls back to the `logging` module directly.
    Controlled by the 'debug-verbose-mode' GSetting.
    """
    from functools import wraps
    import logging
    from gi.repository import Gio

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to get settings and logger from instance
        settings = None
        local_logger = None
        
        if args:
            instance = args[0]
            if hasattr(instance, 'gio_settings'):
                settings = instance.gio_settings
            elif hasattr(instance, 'app') and hasattr(instance.app, 'gio_settings'):
                settings = instance.app.gio_settings
                
            if hasattr(instance, 'logger'):
                local_logger = instance.logger
            elif hasattr(instance, 'app') and hasattr(instance.app, 'logger'):
                local_logger = instance.app.logger

        from ..constants import APP_ID
        
        # If we couldn't find settings on the instance, try to get them globally
        if not settings:
            try:
                settings = Gio.Settings.new(APP_ID)
            except:
                pass

        # If we have settings and debug-verbose-mode is off, just run the function
        if settings and not settings.get_boolean("debug-verbose-mode"):
            return func(*args, **kwargs)

        # Fallback to app logger if no specific logger found
        logger_to_use = local_logger if local_logger else logging.getLogger(APP_ID)

        # Prepare arguments for logging (exclude 'self' for methods)
        log_args = args[1:] if args and hasattr(args[0], '__class__') and isinstance(args[0], object) else args

        logger_to_use.debug(f"Entering: {func.__name__} with args: {log_args} and kwargs: {kwargs}")
        
        result = func(*args, **kwargs)
        
        logger_to_use.debug(f"Exiting: {func.__name__} with return value: {result}")
        return result
    return wrapper
