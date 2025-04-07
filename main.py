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

    - This has been tested on Windows only.

    - If you are having any issues, feel free to email me directly at nick.hanna@onlogic.com.
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
        # Init input handler
        my_dio = HX52xDioHandler()
        
        print("TEST get_di")
        print(my_dio.get_di(0))
        # print(my_dio.get_di(1))
        # print(my_dio.get_di(2))
        # print(my_dio.get_di(3))

        print("TEST get_do")
        print(my_dio.get_do(0))
        # print(my_dio.get_do(1))
        # print(my_dio.get_do(2))
        # print(my_dio.get_do(3))
        
        print("TEST set_do")
        for i in range(0, 1):
            print(my_dio.set_do(i, 1))
            time.sleep(.1)

        for i in range(0, 1):
            print(my_dio.set_do(i, 0))
            time.sleep(.1)

        print("TEST get_di_contact")
        print(my_dio.get_di_contact())

        print("TEST get_do_contact")
        print(my_dio.get_do_contact())

        print("TEST set_di_contact")
        my_dio.set_di_contact(0)

        print("TEST set_di_contact")
        my_dio.set_di_contact(1)

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        del my_dio

if __name__ == "__main__":
    main()
