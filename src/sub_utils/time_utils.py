from datetime import datetime

def get_fuzzy_timestamp(time=False):
    '''
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago', 'just now', etc
    '''
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " s ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " m ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " hrs ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(round(day_diff, 1)) + " days"
    if day_diff < 31:
        weeks = day_diff / 7
        if weeks.is_integer():
            weeks = int(weeks)
        else:
            weeks = round(weeks, 1)
        if weeks == 1:
            return str(weeks) + " week"
        else:
            return str(weeks) + " weeks"
    if day_diff < 365:
        months = day_diff / 30
        if months.is_integer():
            months = int(months)
        else:
            months = round(months, 1)
        if months == 1:
            return str(months) + " month"
        else:
            return str(months) + " months"
    
    return str(round(day_diff / 365, 1)) + " years!!"
