"""
Author: OnLogic
For:    K/HX-52x
Title:  K/HX-52x DIO-Add in Card Python Driver

Description:
    TODO:

Usage:
    python main.py

NOTE: 
    - This program was tested on Python 3.13.0 and Python 3.12.4
    
    - CTRL+C can be used to exit the program.
"""

import timeit # Optional: measure time taken per sample
from DioHandler import DioHandler

def main():
    '''main, implementation of session logic.'''

    # Set to None outside exception handling
    # incase of improper class initialization
    my_dio = None

    try:
        # Init DIO handler
        my_dio = DioHandler(logger_mode="DEBUG", handler_mode="BOTH") #logger_mode="DEBUG", handler_mode="BOTH"
        my_dio.claim()

        # print()
        # print("=" * 30)
        # print("TESTING GET VERSION (GET VERSION)")
        # print(my_dio.get_version())
        # print("=" * 30)
        # print()

        print("=" * 30)
        print("TESTING DIGITAL INPUTS (get_di)")
        print("=" * 30)
        for i in range(8):
            start_time = timeit.default_timer()
            di_val = my_dio.get_di(i)
            print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"DI Channel {i}: {di_val}")
        print()

        exit()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUTS (get_do)")
        print("=" * 30)
        for i in range(8):
            start_time = timeit.default_timer()
            do_val = my_dio.get_do(i)
            print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"DO Channel {i}: {do_val}")
        print()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUTS (set_do)")
        print("=" * 30)
        print("Setting DO channels to 1:")
        for i in range(0, 8):
            start_time = timeit.default_timer()
            result = my_dio.set_do(i, 1)
            print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"Setting DO Channel {i} to 1: Status Code = {result}")
        print("\nSetting DO channels to 0:")
        for i in range(0, 8):
            start_time = timeit.default_timer()
            result = my_dio.set_do(i, 0)
            print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
            print(f"Setting DO Channel {i} to 0: Status Code = {result}")
        print()

        print("=" * 30)
        print("TESTING DIGITAL INPUT CONTACT (get_di_contact)")
        print("=" * 30)
        start_time = timeit.default_timer()
        print(f"DI Contact Status: {my_dio.get_di_contact()}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print()

        print("=" * 30)
        print("TESTING DIGITAL OUTPUT CONTACT (get_do_contact)")
        print("=" * 30)
        start_time = timeit.default_timer()
        print(f"DO Contact Status: {my_dio.get_do_contact()}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print("=" * 30)
        print("Setting DI Contact to 0:")
        start_time = timeit.default_timer()
        print(f"STATUS CODE: {my_dio.set_di_contact(0)}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DI Contact to 0")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL INPUT CONTACT (set_di_contact)")
        print("=" * 30)
        print("Setting DI Contact to 1:")
        start_time = timeit.default_timer()
        print(f"Status Code: {my_dio.set_di_contact(1)}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DI Contact to 1")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL OUTPUT CONTACT (set_do_contact)")
        print("=" * 30)
        print("Setting DO Contact to 0:")
        start_time = timeit.default_timer()
        print(f"Status Code: {my_dio.set_do_contact(0)}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DO Contact to 0")
        print()

        print("=" * 30)
        print("TESTING SET DIGITAL OUTPUT CONTACT (set_do_contact)")
        print("=" * 30)
        print("Setting DO Contact to 1:")
        start_time = timeit.default_timer()
        print(f"STATUS CODE: {my_dio.set_do_contact(1)}")
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")
        print("Set DO Contact to 1")
        print()

        print("=" * 30)
        print("TESTING GET ALL INPUT STATES")
        print("=" * 30)
        start_time = timeit.default_timer()
        print(my_dio.get_all_input_states())
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print("=" * 30)
        print("TESTING GET ALL OUTPUT STATES")
        print("=" * 30)
        start_time = timeit.default_timer()
        print(my_dio.get_all_output_states())
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print("=" * 30)
        print("TESTING SET ALL OUTPUT STATES")
        print("=" * 30)
        start_time = timeit.default_timer()
        print(my_dio.set_all_output_states([0, 1, 0, 1, 0, 0, 0, 1]))
        print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

        print("=" * 30)
        print("TESTING GET ALL INPUT & OUTPUT STATES")
        print("=" * 30)
        for i in range(20):
            start_time = timeit.default_timer()
            print(my_dio.get_all_io_states())
            print(f"The time difference [In Seconds] is : {timeit.default_timer() - start_time:.6f}")

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m")
        if my_dio is not None:
            my_dio.release() 

if __name__ == "__main__":
    main()
