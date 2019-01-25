from dateutil.parser import parse
from croniter import croniter
from datetime import datetime # do no remove this line


def next_run(freq: str, last_run_at):
    if not freq:
        return None
    else:
        if last_run_at is None:
            _d = datetime.now()
        else:
            if isinstance(last_run_at, str):
                _d = parse(last_run_at)
            else:
                _d = last_run_at
        # must indicate day_or as False to make sure the day_of_month/day_of week condition can be satisfied both
        # https://github.com/kiorky/croniter/pull/17
        _iter = croniter(freq, start_time=_d, day_or=False)
        return _iter.get_next(datetime)


if __name__ == '__main__':
    from datetime import datetime

    # print(croniter.is_valid('11 14 */30 * 3#3'))
    # print(croniter.is_valid('11 14 * 1 *'))
    a = croniter('11 14 * * *')
    print(a.get_current(datetime))
    print(a.get_next(datetime))
    print(a.get_next(datetime))
    print(a.get_next(datetime))
    # print(next_run('0 0 */28 * 1,2,3,4,5', None))
    # print(next_run('00 17 */730 */3 2#2', None))
    # print(next_run('11 14 */30 * 3#3', None))
