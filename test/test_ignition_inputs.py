'''
pip install pytest pytest-order

sudo <path/to/venv>/bin/py.test -s -v -x test_ignition.py
python3 
'''

from OnLogicNuvotonManager import AutomotiveHandler
import pytest
import re

@pytest.fixture(scope="module")
def auto_handler():
    return AutomotiveHandler()

@pytest.mark.order(0)
def test_dio_handler_initialization(auto_handler):
    # light claim test, more of this _.py
    with pytest.raises(Exception) as exception_info:
        auto_handler.claim("")

    port = "/dev/ttyS4"
    try:
        auto_handler.claim(port)
    except Exception as e:
        pytest.fail(f"An error occurred in claiming {port}")

def test_crank_values(auto_handler):
    collective_automotive_setting = 1
    while collective_automotive_setting <= (1 << 20):
        print(collective_automotive_setting)
        return_codes = auto_handler.set_all_automotive_settings (
            [
                0, # set_automotive_mode
                0, # set_low_power_enable
                collective_automotive_setting, # set_start_up_timer
                collective_automotive_setting, # set_soft_off_timer
                collective_automotive_setting, # setting_input
                collective_automotive_setting, # set_shutdown_voltage
            ]
        )

        if any( i != 0 for i in return_codes ):
            pytest.fail("Initial set_all_output_states did not successfully execute")

        automitive_setting_dict = auto_handler.get_all_automotive_settings()

        assert automitive_setting_dict["amd"] == 0
        assert automitive_setting_dict["lpe"] == 0
        assert automitive_setting_dict["sut"] == collective_automotive_setting
        assert automitive_setting_dict["sot"] == collective_automotive_setting
        assert automitive_setting_dict["hot"] == collective_automotive_setting
        assert automitive_setting_dict["sdv"] == collective_automotive_setting

        collective_automotive_setting = (collective_automotive_setting << 1)

def test_edge_case_values(auto_handler):
    
    edge_case = [
        0, # set_automotive_mode
        0, # set_low_power_enable
        254, # set_start_up_timer
        254, # set_soft_off_timer
        254, # setting_input
        254, # set_shutdown_voltage
    ]

    for i in range(1, 4):
        return_codes = auto_handler.set_all_automotive_settings(edge_case)

        if any( i != 0 for i in return_codes ):
            pytest.fail("Initial set_all_output_states did not successfully execute")
    
        automitive_setting_dict = auto_handler.get_all_automotive_settings()
        print(automitive_setting_dict)
        assert automitive_setting_dict["amd"] == 0
        assert automitive_setting_dict["lpe"] == 0
        assert automitive_setting_dict["sut"] == edge_case[2]
        assert automitive_setting_dict["sot"] == edge_case[3]
        assert automitive_setting_dict["hot"] == edge_case[4]
        assert automitive_setting_dict["sdv"] == edge_case[5]

        edge_case[2] = edge_case[2] + 1
        edge_case[3] = edge_case[3] + 1
        edge_case[4] = edge_case[4] + 1
        edge_case[5] = edge_case[5] + 1

def edge_case_assertions(func):
    with pytest.raises((TypeError, ValueError)) as e:
        func(-1)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func('a')
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(None)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(8.5)
    print(e)

    with pytest.raises((TypeError, ValueError)) as e:
        func(6.5)
    print(e)

def test_set_automotive_mode(auto_handler):
    edge_case_assertions(auto_handler.set_automotive_mode)

def test_set_low_power_enable(auto_handler):
    edge_case_assertions(auto_handler.set_low_power_enable)

def test_set_start_up_timer(auto_handler):
    edge_case_assertions(auto_handler.set_start_up_timer)

def test_set_soft_off_timer(auto_handler):
    edge_case_assertions(auto_handler.set_soft_off_timer)

def test_set_hard_off_timer(auto_handler):
    edge_case_assertions(auto_handler.set_hard_off_timer)

def test_set_low_voltage_timer(auto_handler):
    edge_case_assertions(auto_handler.set_low_voltage_timer)

def test_get_version(auto_handler):
    version = auto_handler.get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    assert re.match(r"\d.\d.\d", version)
    print(version)

@pytest.mark.order(-1) # execute last
def test_dio_handler_release(auto_handler):
    try:
        auto_handler.release()
    except Exception as e:
        pytest.fail(f"An error Occurred: {e}")