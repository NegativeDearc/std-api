import re


def is_central(segment: str):
    s = re.match(r'P([A-Z]+[0-9]*)', segment)
    return True if s else False


def is_management(segment: str):
    s = re.match(r'P(\d*)$', segment)
    return True if s else False


if __name__ == '__main__':
    assert is_central('P11') == False
    assert is_central('P1') == False
    assert is_central('PV') == True
    assert is_central('PQ') == True
    assert is_central('P11IE') == False
    assert is_central('P') == False
    assert is_management('P') == True
    assert is_management('P1') == True
    assert is_management('P2') == True
    assert is_management('PQ') == False
    assert is_management('PV') == False
    assert is_management('PI') == False
