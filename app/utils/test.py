from cron_descriptor import get_description, Options
from croniter import croniter
from datetime import datetime


def test_cron_expression(cron_string: str, day_or=True):
    options = Options()
    options.locale_code = 'zh_CN'
    base = datetime.now()
    print(get_description(cron_string))
    iter = croniter(cron_string, start_time=base, day_or=day_or)
    print(iter.get_current(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))
    print(iter.get_next(datetime))


if __name__ == '__main__':
    test_cron_expression('00 17 */2 * *', day_or=False)