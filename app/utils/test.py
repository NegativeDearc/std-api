from cron_descriptor import get_description, Options
from croniter import croniter
from datetime import datetime


def test_cron_expression(cron_string: str):
    options = Options()
    options.locale_code = 'zh_CN'
    # print(get_description(cron_string, options))
    base = datetime.now()
    iter = croniter(cron_string, base)
    print(iter.get_prev(datetime))
    print(iter.get_current(datetime))
    print(iter.get_next(datetime))


if __name__ == '__main__':
    test_cron_expression('05 12 */21 * 2,3#1')