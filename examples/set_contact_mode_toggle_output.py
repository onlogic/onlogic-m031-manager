"""
Author: OnLogic
For:    K/HX-52x
Title:  K/HX-52x DIO-add in Card set_contact_mode demonstration

Description:
    A simple demonstration of how to use do concat mode to set the state of digital outputs and then toggle them.

Usage:
    Windows: python set_contact_mode_toggle_output.py

    Linux in venv:
        sudo source/bin/python3 set_contact_mode_toggle_output.py

NOTE: 
    - DIO card must be installed and recognized by the system.

    - If in Linux, please follow instructions in README to set up the virtual environment

    - Press CTRL+C to exit the program.

    - Be sure to run this program with the correct electrical connections.
"""

import time

from DioHandler import DioHandler

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        # Serial port will default to the CDC descriptor of the DIO card if present
        my_dio = DioHandler() 
        my_dio.claim()

        # Set to dry contact mode
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
        print("Exiting...")
        if my_dio is not None:
            my_dio.release() 

if __name__ == "__main__":
    main()
