"""
Author: OnLogic - nick.hanna@onlogic.com, firmwareengineeringteam@onlogic.com
For:    K/HX-52x
Title:  K/HX-52x DIO-Add in Card Python Driver

Description:
    Simple Loopback test for DIO card. This example assumes that the DO pins are looped back to the DI pins with proper electrical connections

Usage:
    Windows:
        python dio_loopback_implementation.py

    Linux in venv:
        sudo source/bin/python3 dio_loopback_implementation.py

NOTE:
    - DIO card must be installed and recognized by the system.

    - If in Linux, please follow instructions in README to set up the virtual environment

    - Press CTRL+C to exit the program.

    - Be sure to run this program with the correct electrical connections.
"""
import time 
from OnLogicM031Manager import DioHandler

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    NUM_PINS = 8
    SLEEP_TIME = 0.1
    ERROR_SLEEP_TIME = 1 
    max_errors_allowed = NUM_PINS * 2

    try:
        # Init DIO handler
        # Serial port will default to the CDC descriptor of the DIO card if present
        my_dio = DioHandler()
        my_dio.claim()

        my_dio.set_di_contact(1)
        my_dio.set_do_contact(1)

        statuses = my_dio.set_all_output_states([0] * NUM_PINS)
        for status in statuses:
            if status < 0:
                print("Failed to set all output states.", status)
                exit(1)

        initial_val = 1
        error_count = 0
        while True:
            for pin in range(NUM_PINS):
                print(f"Setting DO pin {pin} to {initial_val}")
                my_dio.set_do(pin, initial_val)
                di_val = my_dio.get_di(pin)

                print(f"Reading DI pin {pin}, value: {di_val}")
                if di_val != initial_val:
                    error_count += 1

                    print(f"Error: DO pin {pin} set to {initial_val}, but DI reads {di_val}")
                    print("Number of errors: ", error_count, ", Max allowed: ", max_errors_allowed, sep="")
                    if error_count >= max_errors_allowed:
                        print("Too many errors, check connection(s).")
                        exit(1)

                    time.sleep(ERROR_SLEEP_TIME)
                    continue

                time.sleep(SLEEP_TIME)

            initial_val ^= 1

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...")
        if my_dio is not None:
            my_dio.set_all_output_states([0] * NUM_PINS)
            time.sleep(SLEEP_TIME)
            my_dio.release() 

if __name__ == "__main__":
    main()
