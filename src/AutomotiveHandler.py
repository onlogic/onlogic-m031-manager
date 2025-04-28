import time
import serial
from OnLogicNuvotonManager import OnLogicNuvotonManager
from LoggingUtil import logging
from command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices
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
        if(not self.in_valid_range(self.get_soft_off_timer()):
            raise ValueError("Error | Issue with verifying connection command")
        '''

    def _init_port_error_handling(self, error_msg:str, return_early:bool=False) -> None | ValueError:
        self.logger_util._log_print(error_msg, print_to_console=True, color=Fore.RED, log=True,
                                    level=logging.ERROR)
        self.list_all_available_ports()

        if return_early is True:
            return
        
        raise ValueError(error_msg)

    def _init_port(self) -> serial.Serial:
        '''Init port and establish USB-UART connection.'''
        if self.serial_connection_label is None:
            self._init_port_error_handling("ERROR | You must provide a PORT input string for Automotive Mode")
        elif (self.serial_connection_label == self._get_cdc_device_port(ProtocolConstants.DIO_MCU_VID_PID_CDC, ".0")):
            self._init_port_error_handling("Error | DIO COM Port Provided for automotive port entry")
        try:
            return serial.Serial(self.serial_connection_label, 115200, timeout=1)
        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?" \
                                  "Did you enable correct bios settings []?"
            self._init_port_error_handling(serial_connect_err, return_early=True)
            raise serial.SerialException(serial_connect_err)

    def get_automotive_mode(self) -> int:
        automotive_mode = self._construct_command(Kinds.GET_AUTOMOTIVE_MODE)

        self._reset(nack_counter=64)
        if not self._send_command(automotive_mode):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]
    
    def set_automotive_mode(self, mode:int):
        self._validate_input_param(mode, [0,1], int)

        set_auto_mode = self._construct_command(Kinds.SET_AUTOMOTIVE_MODE, mode)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)

        if not self._send_command(set_auto_mode):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, [0,1])

    def get_low_power_enable(self):
        automotive_mode = self._construct_command(Kinds.GET_LOW_POWER_ENABLE)

        self._reset(nack_counter=64)
        if not self._send_command(automotive_mode):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False, log=True, level=logging.DEBUG)

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_low_power_enable(self, lpe_mode:int) -> int:
        self._validate_input_param(lpe_mode, [0,1], int)

        set_lpe_cmd = self._construct_command(Kinds.SET_LOW_POWER_ENABLE, lpe_mode)

        self._reset(nack_counter=64)

        if not self._send_command(set_lpe_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6) 

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, [0,1])
        
    def get_start_up_timer(self) -> int:
        start_up_timer_cmd = self._construct_command(Kinds.GET_START_UP_TIMER)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(start_up_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}", print_to_console=False,
                                    log=True, level=logging.DEBUG)

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, [0,256])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START:payload_end])

    def set_start_up_timer(self, sut:int) -> int:
        self._validate_input_param(sut, [0, 1_000_000], int) #TODO: check 

        set_sut_cmd = self._construct_command(Kinds.SET_START_UP_TIMER, sut.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=64)

        if not self._send_command(set_sut_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1) 
        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, target_indices, [0,256])

    def get_soft_off_timer(self):
        sot_timer_cmd = self._construct_command(Kinds.GET_SOFT_OFF_TIMER)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(sot_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}", print_to_console=False,
                                    log=True, level=logging.DEBUG)

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, [0,256])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START:payload_end])
    
    def set_soft_off_timer(self, sot:int) -> int:
        self._validate_input_param(sot, [0, 1_000_000], int) #TODO: check 

        set_sot_cmd = self._construct_command(Kinds.SET_SOFT_OFF_TIMER, sot.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=64)

        if not self._send_command(set_sot_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1) 
        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False, log=True, level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, target_indices, [0,256])

    def get_hard_off_timer(self):
        hot_timer_cmd = self._construct_command(Kinds.GET_HARD_OFF_TIMER)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(hot_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}", print_to_console=False,
                                    log=True, level=logging.DEBUG)

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, [0,256])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START:payload_end])
    
    def set_hard_off_timer(self, hot:int) -> int:
        self._validate_input_param(hot, [0, 1_000_000], int) #TODO: check 

        set_hot_cmd = self._construct_command(Kinds.SET_HARD_OFF_TIMER, hot.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=64)

        if not self._send_command(set_hot_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(4+8+1) 
        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False, log=True, level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, target_indices, [0,256])

    def get_low_voltage_timer(self): 
        Kinds.GET_LOW_VOLTAGE_TIMER 
    
    def set_low_voltage_timer(self):
        Kinds.SET_LOW_VOLTAGE_TIMER 
    
    def get_shutdown_voltage(self):
        Kinds.GET_SHUTDOWN_VOLTAGE  
    
    def set_shutdown_voltage(self):
        Kinds.SET_SHUTDOWN_VOLTAGE  
