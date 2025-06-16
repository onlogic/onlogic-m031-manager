"""
Author: OnLogic - nick.hanna@onlogic.com, firmwareengineeringteam@onlogic.com
For:    K-52x
Title:  K-52x Shut Down Voltage Example with Logging

Description:
    A simple demonstration of how to use the AutomotiveHandler class to interact with sdv automotive settings.
    This example includes logging functionality to track the operations performed.

Usage:
    python main.py

NOTE: 
    - CTRL+C can be used to exit the program.

    - Be ware of adjusting the automotive values, as they may cause the system to shut down or behave unexpectedly 
      if the proper electrical connections are not made.

    - Please replace "/dev/ttyS4" with the appropriate serial port configured on your system.
"""

from OnLogicM031Manager import AutomotiveHandler
from OnLogicM031Manager import LoggingUtil

import time

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
    # incase of improper class initialization
    my_auto = None

    try:
        # Init DIO handler
        my_auto = AutomotiveHandler()
        my_auto.list_all_available_ports()
        my_auto.claim("/dev/ttyS4") # will be "/dev/ttySX" on Linux or "COMX" on Windows

        print(SEPARATOR)
        print("TESTING GET SHUTDOWN VOLTAGE (get_shutdown_voltage)")
        print("GET SHUT OFF VOLTAGE VALUE:", my_auto.get_shutdown_voltage())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET INPUT VOLTAGE (get_input_voltage)")
        print("GET INPUT VOLTAGE VALUE:", my_auto.get_input_voltage())
        print(SEPARATOR)
        print()

        time.sleep(1)

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...") 
        if my_auto is not None:
            my_auto.release() 

if __name__ == "__main__":
    main()
