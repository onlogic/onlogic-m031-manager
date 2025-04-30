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
    
    - CTRL+C can be used to exit the program.

    set-di-contact  Set digital intput contact type (false:wet, true:dry)
    set-do-contact  Set digital output contact type (false:wet, true:dry)
    set-di-contact  Read digital intput contact type (false:wet, true:dry)
    get-do-contact  Read digital output contact type (false:wet, true:dry)
"""

from DioHandler import DioHandler
import time

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        my_dio = DioHandler() #logger_mode="DEBUG", handler_mode="BOTH"
        my_dio.claim()

        my_dio.set_do_contact(1)
        
        print("DO contact state:", my_dio.get_do_contact())
        i = 0
        while True:
            my_dio.set_do(0, i)
            i ^= 1
            print(i)
            time.sleep(3)

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        if my_dio is not None:
            my_dio.close_connection() 

if __name__ == "__main__":
    main()
