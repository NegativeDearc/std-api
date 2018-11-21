from cron_descriptor import get_description, Options
from croniter import croniter
from datetime import datetime


def test_cron_expression(cron_string: str):
    options = Options()
    options.locale_code = 'zh_CN'
    base = datetime.now()
    iter = croniter(cron_string, start_time=base, day_or=False)
    print(iter.get_prev(datetime))
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
    test_cron_expression('05 13 */1 * 1')
    print('------')
    test_cron_expression('05 13 * * 1')
    print('------')
    test_cron_expression('05 13 1-10 * 1')
