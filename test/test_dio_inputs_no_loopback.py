'''
pip install pytest pytest-order
sudo /home/password/Desktop/titanium-dio-python-driver/bin/py.test -s -v -x test_dio_no_loopback.py
'''
from DioHandler import DioHandler
import pytest
import re

@pytest.fixture(scope="module")
def dio_handler():
    return DioHandler()

@pytest.mark.order(0)
def test_dio_handler_initialization(dio_handler):
    # light claim test, more of this _.py
    with pytest.raises(Exception) as exception_info:
        dio_handler.claim("")

    try:
        dio_handler.claim()
    except Exception as e:
        pytest.fail(f"ERROR, AUTO-LOCK Failed with exception {e}")

def check_for_error(func, error_type, *args):
    with pytest.raises(error_type) as e:
        func(*args)
        print(e)

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
    # test generic error inputs
    edge_case_assertions(dio_handler.set_do)

    for i in range(-1, 9):
        edge_case_assertions(dio_handler.set_do, i)

    # clear output states
    err_codes = dio_handler.set_all_output_states([0 for i in range(8)])
    print(err_codes)
    if any( i != 0 for i in err_codes ):
        pytest.fail("Initial set_all_output_states did not successfully execute")

    target_val = 1
    for pin in range(0, 8):
        error_code = dio_handler.set_do(pin, target_val)
        assert error_code == 0

        do_result = dio_handler.get_do(pin)
        assert do_result == target_val

def test_get_version(dio_handler):
    version = dio_handler.get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    assert re.match(r"\d.\d.\d", version)
    print(version)

def test_set_all_output_states():
    my_dio = DioHandler()
    my_dio.is_setup = True

    # Test for ValueError
    check_for_error(my_dio.set_all_output_states, TypeError, -1)
    check_for_error(my_dio.set_all_output_states, TypeError, None)
    check_for_error(my_dio.set_all_output_states, TypeError, ([None for i in range(8)]))
    check_for_error(my_dio.set_all_output_states, ValueError, [i for i in range(0, 9)])
    check_for_error(my_dio.set_all_output_states, ValueError, [i for i in range(0, 6)])
    check_for_error(my_dio.set_all_output_states, ValueError, ([-1 for i in range(8)]))
    check_for_error(my_dio.set_all_output_states, ValueError, ([2 for i in range(8)]))

    my_dio.is_setup = False