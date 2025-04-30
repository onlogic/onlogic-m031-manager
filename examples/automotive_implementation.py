"""
Author: OnLogic
For:    HX-52x
Title:  HX-52x Automotive Setting Python Utility

Description:
    TODO:

Usage:
    python main.py

NOTE: 
    - This program was tested on Python 3.13.0 and Python 3.12.4
    
    - CTRL+C can be used to exit the program.
"""

from AutomotiveHandler import AutomotiveHandler

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_auto = None

    try:
        # Init DIO handler
        my_auto = AutomotiveHandler() #logger_mode="DEBUG", handler_mode="BOTH"
        my_auto.list_all_available_ports()
        my_auto.claim("/dev/ttyS4") # will be /dev/ttySX" or "COMX" on Windows
                      
        print("=" * 30)
        print("TESTING GET VERSION (get_version)")
        print(my_auto.get_version())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET AUTOMOTIVE MODE (set_automotive_mode)")
        # print("Set Automotive Mode 1, RETURN CODE:", my_auto.set_automotive_mode(1))
        print("SET AUTOMOTIVE MODE, RETURN CODE:", my_auto.set_automotive_mode(0))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET AUTOMOTIVE MODE (get_automotive_mode)")
        print("Automotive Mode:", my_auto.get_automotive_mode())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET LOW POWER ENABLE (set_low_power_enable)")
        print("SET LOW POWER ENABLE RETURN CODE:", my_auto.set_low_power_enable(0))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET LOW POWER ENABLE (get_low_power_enable)")
        print("GET LOW POWER ENABLE VALUE:", my_auto.get_low_power_enable())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET START UP TIMER (set_start_up_timer)")
        print("SET START UP RETURN CODE:", my_auto.set_start_up_timer(10))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET START UP TIMER (get_start_up_timer)")
        print("GET START UP VALUE:", my_auto.get_start_up_timer())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET SOFT OFF TIMER (set_soft_off_timer)")
        print("SET SOFT OFF RETURN CODE:", my_auto.set_soft_off_timer(50))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET SOFT OFF TIMER (get_soft_off_timer)")
        print("GET SOFT OFF VALUE:", my_auto.get_soft_off_timer())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET LOW VOLTAGE TIMER (set_low_voltage_timer)")
        print("SET LOW VOLTAGE RETURN CODE:", my_auto.set_low_voltage_timer(301))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET LOW VOLTAGE TIMER (get_low_voltage_timer)")
        print("GET LOW VOLTAGE TIMER VALUE:", my_auto.get_low_voltage_timer())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET SHUTDOWN VOLTAGE (set_shutdown_voltage)")
        print("SET SHUT OFF VOLTAGE RETURN CODE:", my_auto.set_shutdown_voltage(601))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET SHUTDOWN VOLTAGE (get_shutdown_voltage)")
        print("GET SHUT OFF VOLTAGE VALUE:", my_auto.get_shutdown_voltage())
        print("=" * 30)
        print()

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        if my_auto is not None:
            my_auto.release() 

if __name__ == "__main__":
    main()
