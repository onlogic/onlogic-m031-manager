'''
pip install pytest pytest-order
sudo /home/password/Desktop/titanium-dio-python-driver/bin/py.test -s -v -x test_dio.py
'''
from DioHandler import DioHandler
import pytest
import re

@pytest.fixture(scope="module")
def dio_handler():
    return DioHandler()

@pytest.mark.order(0)
def test_dio_handler_initialization(dio_handler):

    with pytest.raises(Exception) as exception_info:
        dio_handler.claim("")

    try:
        dio_handler.claim()
    except Exception as e:
        pytest.fail(f"ERROR, AUTO-LOCK Failed with exception {e}")

def edge_case_assertions(func, *args):
    with pytest.raises((TypeError, ValueError)) as e:
        func(-1, *args)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func('a', *args)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(None, *args)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(8, *args)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(8.5, *args)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(6.5, *args)
    print(e)

def test_get_di(dio_handler):
    edge_case_assertions(dio_handler.get_di)

def test_get_do(dio_handler):
    edge_case_assertions(dio_handler.get_do)

def test_set_do(dio_handler):
    edge_case_assertions(dio_handler.set_do)
    
    for i in range(-1,8):
        edge_case_assertions(dio_handler.set_do, i)

def test_get_version(dio_handler):
    version = dio_handler.get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    assert re.match(r"\d.\d.\d", version)