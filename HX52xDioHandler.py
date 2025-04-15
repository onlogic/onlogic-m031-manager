'''
File: DioInputHandler.py

Description:
    DioInputHandler administers the serial connection with the
    microcontroller embedded in the add on card of the HX/K5xx.

Contains:
    - class: DioInputHandler
        + private method: __init_port
        + private method: __mcu_connection_check
        + private method: __reset
        + private method: __send_command
        + public method:  get_di

References:
    https://fastcrc.readthedocs.io/en/latest/
'''

import time
import serial
import functools
import logging
import sys

from serial.tools import list_ports as system_ports
from command_set import ProtocolConstants, Kinds, StatusTypes
from fastcrc import crc8
from colorama import Fore, init
from datetime import datetime
from typing import Optional

class HX52xDioHandler():
    '''
    Administers the serial connection with the
    microcontroller embedded in the K/HX-52x DIO-Add in Card.
    '''
    def __init__(self, serial_connection_label:str=None, 
                 logger_mode:str=None, handler_mode:str=None):
        '''Init class by establishing serial connection.'''

        # Init colorama: Color coding for errors and such
        init(autoreset=True) 

        # Setup mechanism so deleter does not delete non-existant object 
        self.is_setup=False   

        # Set up logger 
        self.logger_mode = self.__handle_lconfig_str(logger_mode)
        self.handler_mode = self.__handle_lconfig_str(handler_mode)
        self.__create_logger()

        # Serial device functionality
        self.serial_connection_label = serial_connection_label
        self.port = self.__init_port()
        self.__mcu_connection_check()
        self.is_setup=True
        self.__reset()

    def __del__(self):
        '''Destroy the object and end device communication gracefully.'''
        if self.is_setup:
            self.close_dio_connection()

    def __str__(self):
        '''COM port and command set of DioInputHandler.'''
        # TODO: Add Python utility Version and FW version?
        repr_str = f"Port: {self.serial_connection_label}\n"   \
                   f"Pyserial Version: {serial.__version__}\n" \
                   f"Logger Mode: {self.logger_mode}\n"        \
                   f"Handler Mode: {self.handler_mode}\n"      \
                   f"Main Functionality Setup {self.is_setup}"

        return repr_str

    def __get_device_port(self, dev_id:str, location:str=None) -> str | None:
        """Scan and return the port of the target device."""
        all_ports = system_ports.comports() 
        for port in sorted(all_ports):
            if dev_id in port.hwid:
                if location and location in port.location:
                    self.__log_print(f"Port: {port}\n"
                                     f"Port Location: {port.location}\n"
                                     f"Hardware ID: {port.hwid}\n"
                                     f"Device: {port.device}\n",
                                     log=True,
                                     level=logging.INFO
                                    )
                    return port.device
        return None

    def __init_port(self) -> serial.Serial:
        '''Init port and establish USB-UART connection.'''
        if self.serial_connection_label is None:
            self.serial_connection_label = self.__get_device_port(ProtocolConstants.MCU_VID_PID, ".0")

        try:
            return serial.Serial(self.serial_connection_label, 115200, timeout=1)
        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?"
            self.__log_print(serial_connect_err,
                             print_to_console=True,
                             color=Fore.RED,
                             log=True,
                             level=logging.ERROR
                             )
            raise serial.SerialException(serial_connect_err)

    @staticmethod
    def __handle_lconfig_str(input_str:str) -> str | None:
        return input_str.lower().strip() if isinstance(input_str, str) else input_str

    def __create_logger(self) -> None:
        '''Create Logger with INFO, DEBUG, and ERROR Debugging'''
        if self.logger_mode in [None, "off"]:
            print("Logger Mode off, ignoring")
            return

        if self.logger_mode not in ['info', 'debug','error']:
            print("Logger Mode", self.logger_mode)
            raise ValueError("ERROR | Invalid logger_mode")
        
        now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        filename=f"HX52x_session_{now}.log"

        handlers = []
        if self.handler_mode == "both":
            handlers.extend([logging.FileHandler(filename), 
                            logging.StreamHandler(sys.stdout)])
        elif self.handler_mode == "console":
            handlers.append(logging.StreamHandler(sys.stdout))
        elif self.handler_mode == "file":
            handlers.append(logging.FileHandler(filename))
        else:
            raise ValueError("ERROR | Incorrect Handle Parameter Provided") 
        
        self.logger = logging.getLogger()
    
        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }
        
        level = level_dict.get(self.logger_mode, "Unknown")

        if level == 'Unknown' or level is None:
            self.logger_mode = 'off'
            del self.logger
            raise ValueError("ERROR | Invalid logger_mode")
        
        logging.basicConfig (
            format='[%(asctime)s %(levelname)s %(filename)s %(message)s',
            level=level,
            handlers=handlers  
        )

    @staticmethod
    def __format_log_message(message_info):
        frame = sys._getframe(3)
        lineno = frame.f_lineno
        function = frame.f_code.co_name
        return f":{lineno} -> {function}()] {message_info}"

    def __log_print(self, message_info:str, print_to_console:bool=True, color:str=None, 
                    log:bool=False, level:Optional[int]=None) -> bool:
        if print_to_console and self.logger_mode != "console":
            if color == Fore.RED:
                print(Fore.RED + message_info)
            elif color == Fore.GREEN:
                print(Fore.GREEN + message_info)
            else:
                print(message_info)

        if log is True \
                and level is not None \
                and self.logger_mode not in ["off", None]:

            log_msg = self.__format_log_message(message_info)

            if level == logging.INFO:
                self.logger.info(log_msg)
            elif level == logging.DEBUG:
                self.logger.debug(log_msg)
            elif level == logging.ERROR:
                self.logger.error(log_msg)
            else:
                raise ValueError("ERROR | INCORRECT MODE INPUT INTO LOGGER")

    def __mcu_connection_check(self) -> None:
        '''\
        Check state of MCU, if it returns '\a' successively
        within a proper time interval, the correct port is found.
        '''
        # Local MCU response count
        nack_count = 0

        # Time vals for stopper mechanism
        initial_time = time.time()
        current_time = 0

        self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
        while current_time - initial_time <= ProtocolConstants.TIME_THRESHOLD \
                                             and nack_count < ProtocolConstants.NACKS_NEEDED:

            current_time = time.time()
            if self.port.inWaiting() > 0:
                # If received byte is not what was expected, reset counter
                byte_in_port = self.port.read(1)
                if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_NACK:
                    # print(byte_in_port) # Should be NACKS...
                    nack_count += 1
                    self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(.004)

        if nack_count == ProtocolConstants.NACKS_NEEDED:
            self.__log_print("DIO Interface Found",
                            print_to_console=True,
                            color=Fore.GREEN,
                            log=True,
                            level=logging.INFO
                        )
            return

        self.__log_print(f"ERROR | AKNOWLEDGEMENT ERROR: "\
                         f"mismatch in number of nacks, check if {self.serial_connection_label} "\
                         f"is the right port?",
                         print_to_console=True,
                         color=Fore.RED,
                         log=True,
                         level=logging.ERROR
                        )

        raise ValueError("ERROR | AKNOWLEDGEMENT ERROR")

    def __reset(self, nack_counter:int=ProtocolConstants.NUM_NACKS, reset_buffers:bool=True) -> None:
        '''Reset following the LPMCU ACK-NACK pattern.'''
        # Expensive operation, shouldn't be done twice per read
        if reset_buffers:
            self.port.reset_output_buffer()
            self.port.reset_input_buffer()

        # Send x number of bytes as buffer clear mechanism
        bytes_to_send = nack_counter
        bytes_sent = 0
        while bytes_to_send > 0:
            if bytes_sent > 1024:
                ack_error_msg = f"ERROR | AKNOWLEDGEMENT ERROR: Cannot recover MCU"
                self.__log_print(ack_error_msg,
                                 print_to_console=True,
                                 color=Fore.RED,
                                 log=True,
                                 level=logging.ERROR
                                 )
                
                raise RuntimeError(ack_error_msg)
            
            # Begin buffer clear feedback loop
            self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
            bytes_sent += 1
            byte_in_port = self.port.read(1)

            # If received byte is not what was expected, reset counter
            if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_NACK:
                bytes_to_send -= 1
            else:    
                bytes_to_send = nack_counter

    def __validate_input_param(self, dio_input_parameter, valid_input_range:list, input_type:type):
        if type(dio_input_parameter) != input_type:
            type_error_msg = f"ERROR | {type(dio_input_parameter)} was found when {input_type} was expected"
            
            self.__log_print(type_error_msg,
                            print_to_console=True,
                            color=Fore.RED,
                            log=True,
                            level=logging.ERROR
                            )
            
            raise TypeError(type_error_msg)

        if dio_input_parameter < valid_input_range[0] \
                or dio_input_parameter > valid_input_range[1]:
            value_error_msg = "ERROR | Out of Range Value Provided: " + str(dio_input_parameter) + "." + \
                  " Valid Range " + str(valid_input_range)
            
            self.__log_print(value_error_msg,
                            print_to_console=True,
                            color=Fore.RED,
                            log=True,
                            level=logging.ERROR
                            )
            
            raise ValueError(value_error_msg)

    def __check_crc(self, frame:bytes) -> bool:
        if len(frame) < 4:
            return False
        
        crc_bytes = frame[2:-1]
        crc_val = crc8.smbus(crc_bytes)

        self.__log_print(f"CALCULATED {crc_val} : EXISTING {frame[1]}",
                         print_to_console=False,
                         log=True,
                         level=logging.DEBUG
                        )

        if crc_val != frame[1]:
            self.__log_print(f"CRC MISMATCH",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return False

        return True

    def __validate_recieved_frame(self, return_frame:list, target_index:int=None, target_range:list=None) -> int:
        if return_frame[0] != ProtocolConstants.SHELL_SOF:
            self.__log_print(f"SOF Frame not found",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return StatusTypes.RECV_FRAME_SOF_ERROR

        if return_frame[-1] != ProtocolConstants.SHELL_NACK:
            self.__log_print(f"NACK not found in desired index",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return StatusTypes.RECV_FRAME_NACK_ERROR

        is_crc = self.__check_crc(return_frame)
        if not is_crc:
            self.__log_print(f"CRC Check fail",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return StatusTypes.RECV_FRAME_CRC_ERROR

        if target_index is not None \
                and return_frame[target_index] not in target_range:
            self.__log_print(f"Value at target index not in target range",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return StatusTypes.RECV_NONBINARY_DATATYPE_DETECTED

        return StatusTypes.SUCCESS

    def close_dio_connection(self):
        # HX52xDioHandler.__construct_command.cache_clear()
        # TODO: Figure out why is the sleep function Erroring when lru_cache is enabled 
        # in destructor with time.sleep uncommented 
        # time.sleep(.001)
        self.__reset()
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.close()

    @functools.lru_cache(maxsize=128)
    def __construct_command(self, kind:Kinds, *payload:int) -> bytes:
        # self.__validate_message_bytes(kind, payload)
        
        crc_calculation = crc8.smbus(bytes([len(payload), kind, *payload]))
        
        constructed_command = bytes([ProtocolConstants.SHELL_SOF, 
                                     crc_calculation, 
                                     len(payload), 
                                     kind, 
                                     *payload
                                     ])
        
        self.__log_print(f"Constructed Command {constructed_command}",
                        print_to_console=False,
                        log=True,
                        level=logging.INFO
                        )
        
        return constructed_command

    def __send_command(self, command_to_send:bytes) -> bool:
        # send command byte by byte and validate response
        # print("LEN IS", len(command_to_send), "\n")
        shell_ack_cnt = 0
        for byte in command_to_send:
            self.port.write(byte.to_bytes(1, byteorder='little'))
            byte_in_port = self.port.read(1)

            if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_ACK:
                shell_ack_cnt += 1

        if shell_ack_cnt == len(command_to_send):
            return True 

        self.__log_print(f"ERROR | AKNOWLEDGEMENT ERROR: "\
                         "mismatch in number of aknowledgements, reduce access speed?",
                        print_to_console=False,
                        color=Fore.RED,
                        log=True,
                        level=logging.ERROR
                        )

        return False

    def __receive_command(self, response_frame_len:int=ProtocolConstants.RESPONSE_FRAME_LEN) -> bytes:
        '''\
        receive command in expected format that complies with UART Shell.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.
        '''
        response_frame = []
        self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 
        for _ in range(response_frame_len): 
            byte_in_port = self.port.read(1)
            response_frame.append(byte_in_port)
            self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 
        
        self.__log_print(f"Recieved Command List {response_frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.INFO
                        )

        return b''.join(response_frame)

    def get_di(self, di_pin:int) -> int:
        """\
        User-facing method to get state of digital inputs.

        :param self:    instance of the class
        :param di_pin:  digital input pin with range [0-7]
        :return:        returns 1, indicating on, 0, indicating off, 
                        and -1, indicating an error occured in the sample
        """
        self.__validate_input_param(di_pin, [0,7], int)

        di_command = self.__construct_command(Kinds.GET_DI, di_pin)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(di_command):
            return StatusTypes.SUCCESS

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        # Retrieve do value located in penultimate idx of frame
        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val
        
        return frame[-2]
    
    def get_do(self, do_pin:int) -> int:
        self.__validate_input_param(do_pin, [0,7], int)

        do_command = self.__construct_command(Kinds.GET_DO, do_pin)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        # Retrieve do value located in penultimate idx of frame
        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val
        
        return frame[-2]

    def set_do(self, pin:int, value:int) -> int:
        self.__validate_input_param(pin, [0,7], int)
        self.__validate_input_param(value, [0,1], int)

        set_do_command = self.__construct_command(Kinds.SET_DO, pin, value)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)

        if not self.__send_command(set_do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return StatusTypes.SUCCESS

    def get_di_contact(self) -> int:
        di_contact_state_cmd = self.__construct_command(Kinds.GET_DI_CONTACT)
        
        self.__reset(nack_counter=64)
        if not self.__send_command(di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE
        
        frame = self.__receive_command(6)

        self.__reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[-2]

    def get_do_contact(self) -> int:
        do_contact_state_cmd = self.__construct_command(Kinds.GET_DO_CONTACT)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(do_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE
        
        frame = self.__receive_command(6)
        
        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[-2]

    def set_di_contact(self, contact_type:int) -> int:
        self.__validate_input_param(contact_type, [0,1], int)
        
        set_di_contact_state_cmd = self.__construct_command(Kinds.SET_DI_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)

        if not self.__send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self.__receive_command(6)

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return StatusTypes.SUCCESS

    def set_do_contact(self, contact_type:int) -> int:
        self.__validate_input_param(contact_type, [0,1], int)

        set_di_contact_state_cmd = self.__construct_command(Kinds.SET_DO_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self.__receive_command(6)
                
        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.__log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return StatusTypes.SUCCESS

    def get_all_input_states(self) -> list:
        all_input_states = []
        for i in range(0, 8):
            all_input_states.append(self.get_di(i))

        return all_input_states

    def get_all_output_states(self) -> list:
        all_output_states = []
        
        for i in range(0, 8):
            all_output_states.append(self.get_do(i))

        return all_output_states

    def get_all_io_states(self) -> list:
        return [self.get_all_input_states(), self.get_all_output_states()]

    def set_all_output_states(self, do_lst:list) -> list:
        if len(do_lst) < 8:
            raise ValueError("ERROR | Incorrect amount of inputs specified.")

        error_codes = []
        for do_lst_idx, do_lst_val in enumerate(do_lst):
            error_codes.append(self.set_do(do_lst_idx, do_lst_val))

        return error_codes