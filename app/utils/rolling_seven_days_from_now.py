from dateutil.parser import parse
import datetime


def rolling_seven():
    _now = parse(datetime.datetime.now().strftime('%Y-%m-%d'))
    _past_seven_days = _now - datetime.timedelta(days=7)

    return _past_seven_days, _now


if __name__ == '__main__':
    test = rolling_seven()
    print(test)