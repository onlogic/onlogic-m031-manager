"""
Author: OnLogic
For:    K/HX-52x
Title:  K/HX-52x Automotive Setting Python Utility

Description:
    TODO:

Usage:
    python main.py

NOTE: 
    - This program was tested on Python 3.13.0 and Python 3.12.4
    
    - CTRL+C can be used to exit the program.
"""

import timeit # Optional: measure time taken per sample
from AutomotiveHandler import AutomotiveHandler

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        my_auto = AutomotiveHandler() #logger_mode="DEBUG", handler_mode="BOTH"
        my_auto.claim("COM18")

        print("=" * 30)
        print("TESTING GET VERSION (get_version)")
        print(my_auto.get_version())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET AUTOMOTIVE MODE (get_automotive_mode)")
        print("Automotive Mode:", my_auto.get_automotive_mode())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING SET AUTOMOTIVE MODE (set_automotive_mode)")
        print("Set Automotive Mode 1, Error Code:", my_auto.set_automotive_mode(1))
        print("Set Automotive Mode 0, Error Code:", my_auto.set_automotive_mode(0))
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET LOW POWER ENABLE (get_low_power_enable)")
        print("LOW POWER ENABLE VALUE:", my_auto.get_low_power_enable())
        print("=" * 30)
        print()

        print("=" * 30)
        print("TESTING GET LOW POWER ENABLE (get_low_power_enable)")
        print("LOW POWER ENABLE VALUE:", my_auto.get_low_power_enable())
        print("=" * 30)
        print()

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        if my_dio is not None:
            my_dio.close_connection() 

if __name__ == "__main__":
    main()
