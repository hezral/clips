import logging
import logging
from ..constants import APP_ID
logger = logging.getLogger(APP_ID)
from .logging_utils import log_function_calls


@log_function_calls
def get_widget_by_name(widget, child_name, level, doPrint=False):

    '''
    Function to find widgets using its parent
    https://stackoverflow.com/questions/20461464/how-do-i-iterate-through-all-Gtk-children-in-pyGtk-recursively
    http://cdn.php-Gtk.eu/cdn/farfuture/riUt0TzlozMVQuwGBNNJsaPujRQ4uIYXc8SWdgbgiYY/mtime:1368022411/sites/php-Gtk.eu/files/Gtk-php-get-child-widget-by-name.php__0.txt
    note get_name() vs Gtk.Buildable.get_name(): https://stackoverflow.com/questions/3489520/python-Gtk-widget-name
    '''
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk

    if widget is not None:
        if doPrint: logger.debug("-" * level + str(Gtk.Widget.get_name(widget)) + " :: " + str(type(widget).__name__))
    else:
        if doPrint: logger.debug("-" * level + "None")
        return None

    #/*** If it is what we are looking for ***/
    if(Gtk.Widget.get_name(widget) == child_name): # not widget.get_name() !
        return widget

    #/*** If this widget has one child only search its child ***/
    if (hasattr(widget, 'get_child') and callable(getattr(widget, 'get_child')) and child_name != ""):
        child = widget.get_child()
        if child is not None:
            return get_widget_by_name(child, child_name, level+1, doPrint)

    # /*** It might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children')) and child_name !=""):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = get_widget_by_name(child, child_name, level+1, doPrint) # //search the child
                if found: return found
