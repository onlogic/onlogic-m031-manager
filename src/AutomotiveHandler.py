
from OnLogicNuvotonManager import OnLogicNuvotonManager

import time
import serial

from LoggingUtil import logging
from command_set import ProtocolConstants, Kinds, StatusTypes
from colorama import Fore


class AutomotiveHandler(OnLogicNuvotonManager):
    def __init__(self, logger_mode:str=None, handler_mode:str=None, serial_connection_label=None):
        super().__init__(logger_mode=logger_mode, 
                         handler_mode=handler_mode, 
                         serial_connection_label=serial_connection_label
                        )

    def _mcu_connection_check(self) -> None:
        '''\
        Check state of MCU, if it returns '\a' successively
        within a proper time interval, the correct port is found.
        '''
        super()._mcu_connection_check()
        
        '''
        if(not self.in_valid_range(self.get_softoff_timer()):
            raise ValueError("Error | Issue with verifying connection command")
        '''

    def _init_port(self) -> serial.Serial:
        '''Init port and establish USB-UART connection.'''
        if self.serial_connection_label is None:
            error_msg = "ERROR | You must provide a PORT input string for Automotive Mode"
            self.logger_util._log_print(error_msg, print_to_console=True, color=Fore.RED, log=True,
                                        level=logging.ERROR)
            self.list_all_available_ports()
            raise ValueError(error_msg)
        elif (self.serial_connection_label == self._get_cdc_device_port(ProtocolConstants.DIO_MCU_VID_PID_CDC, ".0")):
            error_msg = "Error | DIO COM Port Provided for automotive port entry"
            self.logger_util._log_print(error_msg, print_to_console=True, 
                                        color=Fore.RED, log=True, level=logging.ERROR)
            self.list_all_available_ports()
            raise ValueError("Error | DIO COM Port Provided for automotive port entry")

        try:
            return serial.Serial(self.serial_connection_label, 115200, timeout=1)
        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?"
            self.logger_util._log_print(serial_connect_err, print_to_console=True, 
                                        color=Fore.RED, log=True, level=logging.ERROR)
            self.list_all_available_ports()
            raise serial.SerialException(serial_connect_err)

    def _format_bytes_to_int_str(self):
        pass

    def get_automotive_mode(self):
        Kinds.GET_AUTOMOTIVE_MODE

    def set_automotive_mode(self):
        Kinds.SET_AUTOMOTIVE_MODE

    def get_low_power_enable(self):
        Kinds.GET_LOW_POWER_ENABLE

    def set_low_power_enable(self):
        Kinds.SET_LOW_POWER_ENABLE

    def get_start_up_timer(self):
        Kinds.GET_START_UP_TIMER

    def set_start_up_timer(self):
        Kinds.SET_START_UP_TIMER

    def get_soft_off_timer(self):
        Kinds.GET_SOFT_OFF_TIMER
    
    def set_soft_off_timer(self):
        Kinds.SET_SOFT_OFF_TIMER

    def get_hard_off_timer(self):
        Kinds.GET_HARD_OFF_TIMER    
    
    def set_hard_off_timer(self):
        Kinds.SET_HARD_OFF_TIMER

    def get_low_voltage_timer(self): 
        Kinds.GET_LOW_VOLTAGE_TIMER 
    
    def set_low_voltage_timer(self):
        Kinds.SET_LOW_VOLTAGE_TIMER 
    
    def get_shutdown_voltage(self):
        Kinds.GET_SHUTDOWN_VOLTAGE  
    
    def set_shutdown_voltage(self):
        Kinds.SET_SHUTDOWN_VOLTAGE  


    # def get_power_state(self):
    #     Kinds.GET_POWER_STATE       

    # def set_power_state(self):
    #     Kinds.SET_POWER_STATE

    '''
    def get_do(self, do_pin:int) -> int:
        self._validate_input_param(do_pin, [0,7], int)

        do_command = self._construct_command(Kinds.GET_DO, do_pin)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command()

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        # Retrieve do value located in penultimate idx of frame
        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[-2]

    def set_do(self, pin:int, value:int) -> int:
        self._validate_input_param(pin, [0,7], int)
        self._validate_input_param(value, [0,1], int)

        set_do_command = self._construct_command(Kinds.SET_DO, pin, value)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)

        if not self._send_command(set_do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command()

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )
    '''
