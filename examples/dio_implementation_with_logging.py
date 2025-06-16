"""
Author: OnLogic - nick.hanna@onlogic.com, firmwareengineeringteam@onlogic.com
For:    K/HX-52x
Title:  K/HX-52x DIO-Add in Card Python Driver with Logging

Description:
    A simple demonstration of how to use the DioHandler class to interact with digital inputs and outputs.

Usage:
    Windows: 
        python dio_implementation.py

    Linux in venv:
        sudo source/bin/python3 dio_implementation_with_logging.py

NOTE:
    - DIO card must be installed and recognized by the system.

    - If in Linux, please follow instructions in README to set up the virtual environment

    - Press CTRL+C to exit the program.

    - Be sure to run this program with the correct electrical connections.
"""

import timeit # Optional: measure time taken per sample
from OnLogicM031Manager import DioHandler
from OnLogicM031Manager import LoggingUtil

def main():
    '''main, implementation of session logic.'''

    SEPARATOR = "=" * 30

    # Initialize logging configuration
    try:
        config_logger = LoggingUtil(
            logger_name='root',
            logger_level="DEBUG",
            handler_mode="CONSOLE",
            log_directory="logs"
        )
        config_logger.config_logger_elements()
    except FileNotFoundError as e:
        print(f"Error configuring logger: {e}")
    except ValueError as e:
        print(f"Error configuring logger: {e}")


    # Set to None outside exception handling
    # in case of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        # Serial port will default to the CDC descriptor of the DIO card if present
        my_dio = DioHandler()
        my_dio.claim()

        print()
        print(SEPARATOR)
        print("TESTING GET VERSION (GET VERSION)")
        print(my_dio.get_version())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING DIGITAL INPUTS (get_di)")
        print(SEPARATOR)
        for i in range(8):
            start_time = timeit.default_timer()
            di_val = my_dio.get_di(i)
            print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"DI Channel {i}: {di_val}")
        print()

        print(SEPARATOR)
        print("TESTING DIGITAL OUTPUTS (get_do)")
        print(SEPARATOR)
        for i in range(8):
            start_time = timeit.default_timer()
            do_val = my_dio.get_do(i)
            print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"DO Channel {i}: {do_val}")
        print()

        print(SEPARATOR)
        print("TESTING DIGITAL OUTPUTS (set_do)")
        print(SEPARATOR)
        print("Setting DO channels to 1:")
        for i in range(0, 8):
            start_time = timeit.default_timer()
            result = my_dio.set_do(i, 1)
            print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"Setting DO Channel {i} to 1: Status Code = {result}")
        print("\nSetting DO channels to 0:")
        for i in range(0, 8):
            start_time = timeit.default_timer()
            result = my_dio.set_do(i, 0)
            print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"Setting DO Channel {i} to 0: Status Code = {result}")
        print()

        print(SEPARATOR)
        print("TESTING DIGITAL INPUT CONTACT (get_di_contact)")
        print(SEPARATOR)
        start_time = timeit.default_timer()
        print(f"DI Contact Status: {my_dio.get_di_contact()}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print()

        print(SEPARATOR)
        print("TESTING DIGITAL OUTPUT CONTACT (get_do_contact)")
        print(SEPARATOR)
        start_time = timeit.default_timer()
        print(f"DO Contact Status: {my_dio.get_do_contact()}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print()

        print(SEPARATOR)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print(SEPARATOR)
        print("Setting DI Contact to 0:")
        start_time = timeit.default_timer()
        print(f"STATUS CODE: {my_dio.set_di_contact(0)}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DI Contact to 0")
        print()

        print(SEPARATOR)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print(SEPARATOR)
        print("Setting DI Contact to 1:")
        start_time = timeit.default_timer()
        print(f"Status Code: {my_dio.set_di_contact(1)}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DI Contact to 1")
        print()

        print(SEPARATOR)
        print("TESTING SET DIGITAL OUTPUT CONTACT (set_do_contact)")
        print(SEPARATOR)
        print("Setting DO Contact to 0:")
        start_time = timeit.default_timer()
        print(f"Status Code: {my_dio.set_do_contact(0)}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DO Contact to 0")
        print()

        print(SEPARATOR)
        print("TESTING SET DIGITAL OUTPUT CONTACT (set_do_contact)")
        print(SEPARATOR)
        print("Setting DO Contact to 1:")
        start_time = timeit.default_timer()
        print(f"STATUS CODE: {my_dio.set_do_contact(1)}")
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DO Contact to 1")
        print()

        print(SEPARATOR)
        print("TESTING GET ALL INPUT STATES")
        print(SEPARATOR)
        start_time = timeit.default_timer()
        print(my_dio.get_all_input_states())
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print(SEPARATOR)
        print("TESTING GET ALL OUTPUT STATES")
        print(SEPARATOR)
        start_time = timeit.default_timer()
        print(my_dio.get_all_output_states())
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print(SEPARATOR)
        print("TESTING SET ALL OUTPUT STATES")
        print(SEPARATOR)
        start_time = timeit.default_timer()
        print(my_dio.set_all_output_states([0, 1, 0, 1, 0, 1, 0, 1]))
        print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print(SEPARATOR)
        print("TESTING GET ALL INPUT & OUTPUT STATES")
        print(SEPARATOR)
        for i in range(5):
            start_time = timeit.default_timer()
            print(my_dio.get_all_io_states())
            print(f"Elapsed Time [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...")
        if my_dio is not None:
            my_dio.release() 

if __name__ == "__main__":
    main()
