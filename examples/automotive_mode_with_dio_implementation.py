"""
Author: OnLogic
For:    K/HX-52x
Title:  K/HX-52x Automotive Mode and DIO Implementation

Description:
    A simple demonstration of how to use the AutomotiveHandler class to interact with automotive settings
    and the DioHandler class to interact with digital inputs and output functions.

    This example combines both functionalities to show how they can work together.

Usage:
    Windows:
        python automotive_mode_with_dio_implementation.py
    Linux in venv:

NOTE: 
    - CTRL+C can be used to exit the program.

    - Be ware of adjusting the automotive values, as they may cause the system to shut down or behave unexpectedly 
      if the proper electrical connections are not made.

    - Please replace "/dev/ttyS4" with the appropriate serial port configured on your system.

    - DIO card must be installed and recognized by the system.

    - If in Linux, please follow instructions in README to set up the virtual environment

    - Press CTRL+C to exit the program.

    - Be sure to run this program with the correct electrical connections.
"""

from OnLogicM031Manager import DioHandler
from OnLogicM031Manager import AutomotiveHandler

def main():
    try:
        with DioHandler() as my_dio:
            # Serial Port must be specified as Class Parameter when using context manager
            with AutomotiveHandler("/dev/ttyS4") as my_auto: 
                print(my_auto.get_all_automotive_settings())
                print(my_dio.get_all_input_states())
    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...") 


if __name__ == "__main__":
    main()
