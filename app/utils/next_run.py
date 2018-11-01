import datetime
from dateutil.parser import parse


def next_run(freq: int,  last_run_time: str):
    _date = datetime.datetime.now() \
        if not last_run_time \
        else parse(last_run_time) if type(last_run_time) == 'str' else last_run_time

    next_run_at = None

    if freq == 0:
        next_run_at = None
    elif freq == 1:
        next_run_at = _date + datetime.timedelta(days=1)
    elif freq == 2:
        next_run_at = _date + datetime.timedelta(days=1)
    elif freq == 3:
        next_run_at = _date + datetime.timedelta(days=7)
    elif freq == 4:
        next_run_at = _date + datetime.timedelta(days=7)

    return next_run_at


if __name__ == '__main__':
    next_run(1, None)
    next_run(4, '2018-10-31')