'''
Assumes the DIO card is connected to the computer 
and the correct  is specified.
'''

from DioHandler import DioHandler
from AutomotiveHandler import AutomotiveHandler
import pytest
import serial

def test_multiple_releases_dio():
    my_dio = DioHandler()
    my_dio.claim()
    my_dio.release()
    my_dio.release()

def test_multiple_claims_dio():
    my_dio = DioHandler()
    my_dio.claim()
    my_dio.claim()
    my_dio.release()

def check_for_error(func, error_type, *args):
    with pytest.raises(error_type) as e:
        func(*args)
        print(e)

def test_multiple_releases_automotive():
    my_auto = AutomotiveHandler()
    my_auto.claim("/dev/ttyS4")
    my_auto.release()
    my_auto.release()
    
def test_multiple_claims_automotive():
    my_auto = AutomotiveHandler()
    check_for_error(my_auto.claim, ValueError)
    check_for_error(my_auto.claim, serial.SerialException, "")

    my_auto.claim("/dev/ttyS4") # Correct port, please replace with correct one
    my_auto.release()

def test_validate_input_param():
    my_dio = DioHandler()
    my_dio.is_setup = True

    input_parameter = 5
    valid_input_range = (0, 7)
    input_type = int

    # validate_input_param will raise an exception if out of range or type error, so we will test two edge cases
    # directly call the function to check for exceptions
    my_dio._validate_input_param(input_parameter, valid_input_range, input_type)
    # Now, test for ValueError
    check_for_error(my_dio._validate_input_param, ValueError, -1, valid_input_range, input_type)
    check_for_error(my_dio._validate_input_param, ValueError, 8, valid_input_range, input_type)
    for i in range(0, 8):
        my_dio._validate_input_param(i, valid_input_range, input_type)

    # Test for TypeError
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, str)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, float)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, list)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, dict)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, tuple)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, set)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, bool)
    check_for_error(my_dio._validate_input_param, TypeError, input_parameter, valid_input_range, None)
    check_for_error(my_dio._validate_input_param, TypeError, 7.5, valid_input_range, input_type)
    check_for_error(my_dio._validate_input_param, TypeError, 5.5, valid_input_range, input_type)
    my_dio.is_setup = False

def test_within_valid_range():
    my_dio = DioHandler()
    my_dio.is_setup = True

    frame = b'\x01\x02\x03\x04\x05'
    index_range = [i for i in range(0, 4)]
    value_range = (0, 4)

    # first test several individual indices
    for frame_idx in index_range:
        print(f"\nFrame idx {frame_idx} : Value {frame[frame_idx]}, valid range {value_range}")
        my_dio._within_valid_range(frame, frame_idx, value_range)
        assert my_dio._within_valid_range(frame, frame_idx, value_range) == True
    assert my_dio._within_valid_range(frame, 4, value_range) == False
    assert my_dio._within_valid_range(frame, -1, value_range) == False

    # now test for tuple index
    index_range = (2, 4)
    my_dio._within_valid_range(frame, index_range, value_range)
    assert my_dio._within_valid_range(frame, index_range, value_range) == True    

    my_dio.is_setup = False

def test_context_manager():
    my_dio = DioHandler()
    my_dio.claim()
    assert my_dio.is_setup == True
    with my_dio:
        assert my_dio.is_setup == True
    assert my_dio.is_setup == False
    my_dio.release()
    assert my_dio.is_setup == False

def test_context_manager_both():
    with DioHandler() as my_dio:
        with AutomotiveHandler("/dev/ttyS4") as my_auto:
            assert my_dio.is_setup == True
            assert my_auto.is_setup == True
            print(my_auto.set_all_automotive_settings([0, 0, 5, 5, 10, 600]))

            print(my_auto.get_all_automotive_settings())
            print(my_dio.get_all_input_states())
    assert my_dio.is_setup == False
    assert my_auto.is_setup == False