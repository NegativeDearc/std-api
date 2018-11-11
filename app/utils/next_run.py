import datetime
from dateutil.parser import parse


def next_run(freq: str, last_run_at):
    if not freq:
        return None
    else:
        week_index = freq.split(',')
        if last_run_at is None:
            _d = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            if isinstance(last_run_at, str):
                _d = parse(last_run_at) + datetime.timedelta(days=1)
            else:
                _d = last_run_at + datetime.timedelta(days=1)

        while not _d.strftime('%w') in week_index:
            _d = _d + datetime.timedelta(days=1)
        return parse(_d.strftime('%Y-%m-%d'))


if __name__ == '__main__':
    print(next_run('4,3,2,5', datetime.datetime.now()))
