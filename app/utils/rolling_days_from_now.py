from dateutil.parser import parse
import datetime


def rolling_days(days: int = 7):
    _now = parse(datetime.datetime.now().strftime('%Y-%m-%d'))
    _past_seven_days = _now - datetime.timedelta(days=days)

    return _past_seven_days, _now


if __name__ == '__main__':
    test = rolling_days()
    print(test)