
#-------------------------------------------------------------------------------------------------------

from datetime import timedelta
from functools import wraps
from timeit import default_timer as timer
# from typing import Any, Callable, Optional # Not used in code below but good for signatures if added

# def metrics(func: Optional[Callable] = None, name: Optional[str] = None, hms: Optional[bool] = False) -> Any:
def metrics(func=None, name=None, hms=False, logger=None):
    """Decorator to show execution time.

    :param func: Decorated function
    :param name: Metrics name
    :param hms: Show as human-readable string
    """
    assert callable(func) or func is None

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            comment = f"execution time of {name or fn.__name__}:"
            t = timer()
            result = fn(*args, **kwargs)
            te = timer() - t

            # from common import log
            # logger = log.withPrefix('[METRICS]')
            if logger:
                if hms:
                    logger.debug(f"{comment} {timedelta(seconds=te)}")
                else:
                    logger.debug(f"{comment} {te:>.6f} sec")

            return result
        return wrapper

    return decorator(func) if callable(func) else decorator

#-------------------------------------------------------------------------------------------------------

def run_async(func):
    '''
    https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
    http://code.activestate.com/recipes/576683-simple-threading-decorator/
    run_async(func): 
    function decorator, intended to make "func" run in a separate thread (asynchronously).
    Returns the created Thread object
    Example:
        @run_async
        def task1():
            do_something
        @run_async
        def task2():
            do_something_too
    '''
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        # Never return anything, idle_add will think it should re-run the
        # function because it's a non-False value.
        return None

    return async_func
