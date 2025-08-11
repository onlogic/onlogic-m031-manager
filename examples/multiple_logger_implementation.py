"""
Author: OnLogic - nick.hanna@onlogic.com, firmwareengineeringteam@onlogic.com
For:    K-52x
Title:  K-52x Logging Multiple Logger Implementation Example

Description:
    A simple demonstration of how to use several loggers in a simple implementation across multiple classes.

Usage:
    Windows:
        python automotive_implementation_sdv_with_logging.py
    
    Linux in venv: 
        sudo source/bin/python3 automotive_implementation_sdv_with_logging.py    

NOTE: 
    - CTRL+C can be used to exit the program.

    - Be ware of adjusting the automotive values, as they may cause the system to shut down or behave unexpectedly 
      if the proper electrical connections are not made.

    - Please replace "/dev/ttyS4" with the appropriate serial port configured on your system.
"""

from OnLogicM031Manager import DioHandler
from OnLogicM031Manager import AutomotiveHandler

import logging
import time

import time

def main():
    '''main, implementation of session logic.'''

    SEPARATOR = "=" * 30

    from OnLogicM031Manager.logging_util import LoggingUtil

    # Initialize logging configurations
    try:
        # 1. Configure the root logger to INFO to see messages from this script.
        LoggingUtil('root', 'info', 'console').config_logger_elements()
        
        # 2. These loggers remain independent and will only show ERROR messages.
        LoggingUtil('OnLogicM031Manager.dio_handler', 'error', 'console').config_logger_elements()
        LoggingUtil('OnLogicM031Manager.automotive_handler', 'error', 'console').config_logger_elements()
        
        # 3. This logger will only show DEBUG messages.
        LoggingUtil('OnLogicM031Manager.onlogic_m031_manager', 'error', 'console').config_logger_elements()

        # Get the logger for use in this file (__main__)
        main_logger = logging.getLogger(__name__)

    except FileNotFoundError as e:
        print(f"Error configuring logger: {e}")
    except ValueError as e:
        print(f"Error configuring logger: {e}")

    # Set to None outside exception handling
    # incase of improper class initialization
    my_auto = None
    my_dio = None

    try:
        # Init MCU Handlers
        my_dio = DioHandler()
        my_auto = AutomotiveHandler(serial_connection_label="/dev/ttyS4") # will be "/dev/ttySX" on Linux or "COMX" on Windows

        my_dio.claim() 
        my_auto.claim()

        # set dio contact to wet
        my_dio.set_di_contact(0) 
        my_dio.set_do_contact(0)

        pin_val = 1
        main_logger.info(f"\nSetting DO channels to {pin_val}")
        for i in range(0, 8):
            result = my_dio.set_do(i, pin_val)
            main_logger.info(f"Setting DO Channel {i} to 1: Status Code = {result}")

        pin_val = 0
        main_logger.info(f"\nSetting DO channels to {pin_val}")
        for i in range(0, 8):
            result = my_dio.set_do(i, pin_val)
            main_logger.info(f"Setting DO Channel {i} to 0: Status Code = {result}")
        print()

        ### AUTOMOTIVE FUNCTIONALITY ###
        print(SEPARATOR)
        main_logger.info("TESTING GET SHUTDOWN VOLTAGE (get_shutdown_voltage)")
        main_logger.info(f"GET SHUT OFF VOLTAGE VALUE: {my_auto.get_shutdown_voltage()}")
        main_logger.info(SEPARATOR)
        print()

        print(SEPARATOR)
        main_logger.info("TESTING GET INPUT VOLTAGE (get_input_voltage)")
        main_logger.info(f"GET INPUT VOLTAGE VALUE: {my_auto.get_input_voltage()}")
        print(SEPARATOR)
        print()

        time.sleep(1)

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...") 
        if my_auto is not None:
            my_auto.release() 
        
        if my_dio is not None:
            my_dio.release()

if __name__ == "__main__":
    main()
