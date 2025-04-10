"""
Author: OnLogic
For:    K/HX-52x
Title:  K/HX-52x DIO-Add in Card Python Driver

Description:
    TODO:

Dependencies:
    1. pyserial: 
        pip3 install pyserial

    2. colorama 
        pip3 install colorama

Usage:
    python main.py

NOTE: 
    - This program was tested on Python 3.13.0 and Python 3.12.4

    - TODO: Automatically find and latch on to the dio terminal using HW serial methods
    
    - CTRL+C can be used to exit the program.

    - There is a time.sleep(.004) delay in get_di for stabilization.
"""

import timeit # Optional: measure time taken per sample
from HX52xDioHandler import HX52xDioHandler
import time

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        my_dio = HX52xDioHandler() #logger_mode="DEBUG", handler_mode="BOTH"
        
        print("=" * 30)
        print("TESTING DIGITAL INPUTS (get_di)")
        print("=" * 30)
        for i in range(8):
            print(f"DI Channel {i}: {my_dio.get_di(i)}")
            time.sleep(.1)
        print()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUTS (get_do)")
        print("=" * 30)
        for i in range(8):
            print(f"DO Channel {i}: {my_dio.get_do(i)}")
            time.sleep(.01)
        print()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUTS (set_do)")
        print("=" * 30)
        print("Setting DO channels to 1:")
        for i in range(0, 8):
            result = my_dio.set_do(i, 1)
            print(f"Setting DO Channel {i} to 1: Result = {result}")
            time.sleep(.1)       
        print("\nSetting DO channels to 0:")
        for i in range(0, 8):
            result = my_dio.set_do(i, 0)
            print(f"Setting DO Channel {i} to 0: Result = {result}")
            time.sleep(.1)
        print()
        
        print("=" * 30)
        print("TESTING DIGITAL INPUT CONTACT (get_di_contact)")
        print("=" * 30)
        print(f"DI Contact Status: {my_dio.get_di_contact()}")
        print()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUT CONTACT (get_do_contact)")
        print("=" * 30)
        print(f"DO Contact Status: {my_dio.get_do_contact()}")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print("=" * 30)
        print("Setting DI Contact to 1:")
        my_dio.set_di_contact(0)
        print("Set DI Contact to 1")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print("=" * 30)
        print("Setting DI Contact to 0:")
        my_dio.set_di_contact(1)
        print("Set DI Contact to 0")
        print()

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        del my_dio

if __name__ == "__main__":
    main()
