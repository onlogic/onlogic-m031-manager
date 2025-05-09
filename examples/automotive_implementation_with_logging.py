"""
Author: OnLogic
For:    HX-52x/K-52x
Title:  HX-52x/K-52x Automotive Driver Example with Logging

Description:
    A simple demonstration of how to use the AutomotiveHandler class to interact with automotive settings.
    This example includes logging functionality to track the operations performed.

Usage:
    python main.py

NOTE: 
    - CTRL+C can be used to exit the program.

    - Be ware of adjusting the automotive values, as they may cause the system to shut down or behave unexpectedly 
      if the proper electrical connections are not made.

    - Please replace "/dev/ttyS4" with the appropriate serial port configured on your system.
"""

from OnLogicNuvotonManager import AutomotiveHandler
from OnLogicNuvotonManager import LoggingUtil

def main():
    '''main, implementation of session logic.'''

    SEPARATOR = "=" * 30

    # Initialize logging configuration
    try:
        config_logger = LoggingUtil(
            logger_name='root',
            logger_level="DEBUG",
            handler_mode="CONSOLE"
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
        print("TESTING GET VERSION (get_version)")
        print(my_auto.get_version())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET AUTOMOTIVE MODE (set_automotive_mode)")
        # print("Set Automotive Mode 1, RETURN CODE:", my_auto.set_automotive_mode(1))
        print("SET AUTOMOTIVE MODE, RETURN CODE:", my_auto.set_automotive_mode(0))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET AUTOMOTIVE MODE (get_automotive_mode)")
        print("Automotive Mode:", my_auto.get_automotive_mode())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET LOW POWER ENABLE (set_low_power_enable)")
        print("SET LOW POWER ENABLE RETURN CODE:", my_auto.set_low_power_enable(0))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET LOW POWER ENABLE (get_low_power_enable)")
        print("GET LOW POWER ENABLE VALUE:", my_auto.get_low_power_enable())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET START UP TIMER (set_start_up_timer)")
        print("SET START UP RETURN CODE:", my_auto.set_start_up_timer(12))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET START UP TIMER (get_start_up_timer)")
        print("GET START UP VALUE:", my_auto.get_start_up_timer())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET SOFT OFF TIMER (set_soft_off_timer)")
        print("SET SOFT OFF RETURN CODE:", my_auto.set_soft_off_timer(51))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET SOFT OFF TIMER (get_soft_off_timer)")
        print("GET SOFT OFF VALUE:", my_auto.get_soft_off_timer())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET LOW VOLTAGE TIMER (set_low_voltage_timer)")
        print("SET LOW VOLTAGE RETURN CODE:", my_auto.set_low_voltage_timer(301))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET LOW VOLTAGE TIMER (get_low_voltage_timer)")
        print("GET LOW VOLTAGE TIMER VALUE:", my_auto.get_low_voltage_timer())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET SHUTDOWN VOLTAGE (set_shutdown_voltage)")
        print("SET SHUT OFF VOLTAGE RETURN CODE:", my_auto.set_shutdown_voltage(601))
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET SHUTDOWN VOLTAGE (get_shutdown_voltage)")
        print("GET SHUT OFF VOLTAGE VALUE:", my_auto.get_shutdown_voltage())
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING SET ALL AUTOMOTIVE SETTINGS (set_all_automotive_settings)")
        print(
            "[amd, lpe, sut, sot, hot, sdv]",
            my_auto.set_all_automotive_settings(setting_input = [
                    0,  # amd 
                    0,  # lpe 
                    10, # sut 
                    50, # sot 
                    30, # hot 
                    600 # sdv
                ]
            ),
            sep = '\n'
        )
        print(SEPARATOR)
        print()

        print(SEPARATOR)
        print("TESTING GET ALL AUTOMOTIVE SETTINGS (get_all_automotive_settings)")
        my_auto.get_all_automotive_settings(output_to_console=True)
        print(SEPARATOR)
        print()

    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("Exiting...") 
        if my_auto is not None:
            my_auto.release() 

if __name__ == "__main__":
    main()
