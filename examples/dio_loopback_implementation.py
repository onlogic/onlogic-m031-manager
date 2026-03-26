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

    # --- Test Configuration ---
    STOP_ON_MAX_ERROR = True   # Set to True to stop at MAX_ERRORS_ALLOWED, False to run infinitely
    MAX_ERRORS_ALLOWED = 16     # Only applies if STOP_ON_MAX_ERROR is True
    NUM_PINS = 8
    SLEEP_TIME = 0.1
    ERROR_SLEEP_TIME = 1 

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

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
        attempt_count = 0
        
        run_test = True
        while run_test:
            for pin in range(NUM_PINS):
                print(f"Setting DO pin {pin} to {initial_val}")
                attempt_count += 1
                my_dio.set_do(pin, initial_val)
                di_val = my_dio.get_di(pin)

                print(f"Reading DI pin {pin}, value: {di_val}")
                if di_val != initial_val:
                    error_count += 1

                    print(f"Error: DO pin {pin} set to {initial_val}, but DI reads {di_val}")
                    print(f"Total errors so far: {error_count}")

                    # Evaluates the new boolean
                    if STOP_ON_MAX_ERROR and error_count >= MAX_ERRORS_ALLOWED:
                        print(f"\nMax errors ({MAX_ERRORS_ALLOWED}) reached. Terminating test.")
                        run_test = False
                        break 

                    time.sleep(ERROR_SLEEP_TIME)
                    continue

                time.sleep(SLEEP_TIME)

            if run_test:
                initial_val ^= 1

        print(f"\nTest Summary -> Total attempts: {attempt_count}, Total errors: {error_count}")

    except KeyboardInterrupt:
        print("\nOperation terminated by user.")
        print(f"Test Summary -> Total attempts: {attempt_count}, Total errors: {error_count}")
    finally: 
        print("Exiting...")
        if my_dio is not None:
            my_dio.set_all_output_states([0] * NUM_PINS)
            time.sleep(SLEEP_TIME)
            my_dio.release() 

if __name__ == "__main__":
    main()