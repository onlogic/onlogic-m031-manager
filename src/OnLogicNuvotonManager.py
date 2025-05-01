'''
File: OnLogicNuvotonManager.py

Description:
    OnLogicNuvotonManager administers the serial connection with the
    microcontroller embedded in the add on card of the HX/K5xx.

Contains:
    - class: OnLogicNuvotonManager
        + private method: _init_port
        + private method: _mcu_connection_check
        + private method: _reset
        + private method: _send_command
        
References:
    https://fastcrc.readthedocs.io/en/latest/
'''

import time
import serial
import functools
from abc import ABC, abstractmethod
from LoggingUtil import LoggingUtil, logging
from serial.tools import list_ports as system_ports
from command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices, BoundaryTypes
from fastcrc import crc8
from colorama import Fore, init

class OnLogicNuvotonManager(ABC):
    '''
    Administers the serial connection with the
    microcontroller embedded in the K/HX-52x DIO-Add and Sequence MCU for Automotive Control.
    '''
    def __init__(self, logger_mode: str = None, handler_mode: str = None, serial_connection_label: str = None):
        '''Init class by establishing serial connection.'''
        # Init colorama: Color coding for errors and such
        init(autoreset=True) 

        # Setup mechanism so deleter does not delete non-existant objects
        self.is_setup=False

        # Set up logger
        logger_mode = self.__handle_lconfig_str(logger_mode)
        handler_mode = self.__handle_lconfig_str(handler_mode)

        self.logger_util = LoggingUtil(logger_mode, handler_mode)
        self.logger_util._create_logger()

        self.serial_connection_label = serial_connection_label

    def __enter__(self):
        self.claim()
        return self

    def __exit__(self, etype, evalue, etraceback):
        self.release()

    def __del__(self):
        '''Destroy the object and end device communication gracefully.'''
        self.release()

    def __str__(self):
        '''COM port and command set of DioInputHandler.'''
        # TODO: Add Python utility Version and FW version?
        repr_str = (
            f"Port: {self.serial_connection_label}\n"
            f"PySerial Version: {serial.__version__}\n"
            f"Main Functionality Setup: {self.is_setup}\n"
            f"Command Set: {Kinds.__name__}\n"
            f"Protocol Constants: {ProtocolConstants.__name__}\n"
            f"Status Types: {StatusTypes.__name__}\n"
            f"Target Indices: {TargetIndices.__name__}\n"
            f"Boundary Types: {BoundaryTypes.__name__}\n"
            f"Serial Connection Label: {self.serial_connection_label}\n"
            f"Serial Port: {self.port if hasattr(self, 'port') else 'Serial Port not initialized'}\n"
            f"Is Setup: {self.is_setup}\n"
        )

        return repr_str

    @staticmethod
    def __handle_lconfig_str(input_str: str) -> str | None:
        return input_str.lower().strip() if isinstance(input_str, str) else input_str

    def list_all_available_ports(self, verbose: bool = False):
        all_ports = system_ports.comports()
        for port in sorted(all_ports):
            if not verbose:
                self.logger_util._log_print(port, log=True, level=logging.INFO)
            elif verbose:
                self.logger_util._log_print(f"Port: {port}\n"
                                            f"Port Location: {port.location}\n"
                                            f"Hardware ID: {port.hwid}\n"
                                            f"Device: {port.device}\n",
                                            print_to_console=False,
                                            log=True, level=logging.INFO)  

    def _get_cdc_device_port(self, dev_id: str, location: str = None) -> str | None:
        """Scan and return the port of the target device."""
        all_ports = system_ports.comports() 
        for port in sorted(all_ports):
            if dev_id in port.hwid:
                if location and location in port.location:
                    self.logger_util._log_print(f"NOTE | DIO CARD FOUND ON:\n"
                                                f"Port: {port}\n"
                                                f"Port Location: {port.location}\n"
                                                f"Hardware ID: {port.hwid}\n"
                                                f"Device: {port.device}\n",
                                                log=True, level=logging.INFO)
                    return port.device
        return None

    @abstractmethod
    def get_info(self) -> None:
        pass

    @abstractmethod
    def _init_port(self) -> serial.Serial:
        '''\
        Initialize the serial port with the given baudrate and device descriptor.
        If the port is not specified, it will search for the device with the 
        given VID and PID when used for DIO Utility. Otherwise, it will simply initialize
        the port with the given serial connection label.

        If the port is not found, it will raise a ValueError.
        '''

        pass

    @abstractmethod
    def _mcu_connection_check(self) -> None:
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
                    self.logger_util._log_print(f"{byte_in_port}",print_to_console=False, log=True, level=logging.DEBUG)
                    nack_count += 1
                    self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(ProtocolConstants.STANDARD_DELAY)

        if nack_count == ProtocolConstants.NACKS_NEEDED:
            self.logger_util._log_print("Interface Found", print_to_console=True, 
                                        color=Fore.GREEN, log=True, level=logging.INFO)
            return

        self.logger_util._log_print(f"ERROR | AKNOWLEDGEMENT ERROR: "\
                                    f"mismatch in number of nacks, check if {self.serial_connection_label} " \
                                    f"is the right port?", print_to_console=True, 
                                    color=Fore.RED, log=True, level=logging.ERROR)

        self.list_all_available_ports()

        raise ValueError("ERROR | AKNOWLEDGEMENT ERROR")

    def _read_files(self, filename = None) -> None:
        pass

    def _reset(self, nack_counter: int = ProtocolConstants.NUM_NACKS, reset_buffers: bool = True) -> None:
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
                self.logger_util._log_print(ack_error_msg, print_to_console=True, 
                                            color=Fore.RED, log=True, level=logging.ERROR
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

    def _validate_input_param(self, dio_input_parameter, valid_input_range: tuple, input_type: type):
        if self.is_setup is False:
            raise serial.SerialException("ERROR | Serial Connection is not set up, did you claim the port?")

        if type(dio_input_parameter) != input_type:
            type_error_msg = f"ERROR | {type(dio_input_parameter)} was found when {input_type} was expected"

            self.logger_util._log_print(type_error_msg, print_to_console=True, 
                                        color=Fore.RED, log=True, level=logging.ERROR)

            raise TypeError(type_error_msg)

        if dio_input_parameter < valid_input_range[0] \
                or dio_input_parameter > valid_input_range[1]:
            value_error_msg = "ERROR | Out of Range Value Provided: " + str(dio_input_parameter) + "." + \
                              " Valid Range " + str(valid_input_range)

            self.logger_util._log_print(value_error_msg, print_to_console=True, 
                                        color=Fore.RED, log=True, level=logging.ERROR)

            raise ValueError(value_error_msg)

    def _check_crc(self, frame: bytes) -> bool:
        if len(frame) < BoundaryTypes.BASE_FRAME_SIZE:
            return False

        # add 1 make penultimate index the last value in slice
        crc_bytes = frame[TargetIndices.RECV_PAYLOAD_LEN: TargetIndices.PENULTIMATE+1] 
        
        crc_val = crc8.smbus(crc_bytes)

        self.logger_util._log_print(f"CALCULATED {crc_val} : EXISTING {frame[TargetIndices.CRC]}",
                                    print_to_console=False, log=True, level=logging.DEBUG)

        if crc_val != frame[TargetIndices.CRC]:
            self.logger_util._log_print(f"CRC MISMATCH",
                             color=Fore.RED,
                             print_to_console=True,
                             log=True,
                             level=logging.ERROR
                            )
            return False

        return True

    def _within_valid_range(self, return_frame: bytes, target_index: int | tuple, target_range: tuple) -> bool:        
        if isinstance(target_index, int):
            if return_frame[target_index] < target_range[0] or \
                    return_frame[target_index] > target_range[1]:
                return False
            
        elif isinstance(target_index, tuple):
            payload_indices_to_check = [p_idx for p_idx in range(target_index[0], target_index[1])]
            for payload_idx in payload_indices_to_check:
                if return_frame[payload_idx] < target_range[0] or \
                        return_frame[payload_idx] > target_range[1]:
                    return False
        return True

    def _validate_recieved_frame(self, return_frame: list, target_index: int | tuple = None, target_range: tuple = None) -> int:
        if return_frame[TargetIndices.SOF] != ProtocolConstants.SHELL_SOF:
            self.logger_util._log_print(f"SOF Value Not Correct", color=Fore.RED, print_to_console=True,
                                        log=True,level=logging.ERROR)
            return StatusTypes.RECV_FRAME_SOF_ERROR

        if return_frame[TargetIndices.NACK] != ProtocolConstants.SHELL_NACK:
            self.logger_util._log_print(f"NACK Not Found in Desired Index", color=Fore.RED,
                                        print_to_console=True, log=True, level=logging.ERROR)
            return StatusTypes.RECV_FRAME_NACK_ERROR
    
        """
        TODO: come up with some condition to check len
        if return_frame[2] ...
        """

        is_crc = self._check_crc(return_frame)
        if not is_crc:
            self.logger_util._log_print(f"CRC Check fail", color=Fore.RED, print_to_console=True,
                                        log=True, level=logging.ERROR)

            return StatusTypes.RECV_FRAME_CRC_ERROR

        if target_index is not None \
                and not self._within_valid_range(return_frame, target_index, target_range): 
            self.logger_util._log_print(f"Value(s) at idx {target_index} not in target range: {target_range}",
                                        color=Fore.RED, print_to_console=True, log=True, level=logging.ERROR)
            return StatusTypes.RECV_UNEXPECTED_PAYLOAD_ERROR

        return StatusTypes.SUCCESS

    def claim(self, serial_connection_label=None):
        # Serial device functionality
        if serial_connection_label is not None:
            self.serial_connection_label = serial_connection_label

        self.port = self._init_port()
        self._mcu_connection_check()
        self.is_setup = True
        self._reset()

    def release(self):
        # ._construct_command.cache_clear()

        # TODO: Figure out why is the sleep function Erroring when lru_cache is enabled 
        # in destructor with time.sleep uncommented 
        # time.sleep(.001)
        if self.is_setup:
            self._reset()
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            self.port.close()
            self.is_setup = False

    @functools.lru_cache(maxsize=128)
    def _construct_command(self, kind: Kinds, *payload: int) -> bytes:
        # Construct command in the format of [SOF, CRC, LEN, KIND, PAYLOAD]
        # self.validate_message_bytes(kind, payload)
        if len(payload) > 0 and isinstance(payload[0], bytes):
            payload_bytes, payload_length = payload[0], payload[1]

            crc_calculation = crc8.smbus(bytes([payload_length, kind]) + payload_bytes)

            constructed_command = bytes([ProtocolConstants.SHELL_SOF, 
                                        crc_calculation, 
                                        payload_length, 
                                        kind,
                                        ]) + payload_bytes
        else:
            crc_calculation = crc8.smbus(bytes([len(payload), kind, *payload]))

            constructed_command = bytes([ProtocolConstants.SHELL_SOF, 
                                        crc_calculation, 
                                        len(payload), 
                                        kind, 
                                        *payload
                                        ])

        self.logger_util._log_print(f"Constructed Command {constructed_command}",
                                    print_to_console=False, log=True, level=logging.INFO)
        
        return constructed_command

    def _send_command(self, command_to_send: bytes) -> bool:
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

        self.logger_util._log_print(f"ERROR | AKNOWLEDGEMENT ERROR: "\
                         "mismatch in number of aknowledgements, reduce access speed?",
                        print_to_console=False, color=Fore.RED, log=True, level=logging.ERROR)

        return False

    '''
    def _receive_command(self, response_frame_len: int = ProtocolConstants.RESPONSE_FRAME_LEN) -> bytes:
        
        receive command in expected format that complies with UART Shell.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.
        
        response_frame = []
        self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 
        for _ in range(response_frame_len): 
            byte_in_port = self.port.read(1)
            response_frame.append(byte_in_port)
            self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 

        self.logger_util._log_print(f"Recieved Command List {response_frame}",
                                    print_to_console=False, log=True, level=logging.INFO)

        return b''.join(response_frame)
    '''

    def _validate_partial_frame(self, response_frame: list, response_frame_kind: int) -> bool:
        '''\
        Validate the partial frame (first four bytes) received from the MCU UT.
        '''
        response_frame_size = len(response_frame)
        if response_frame_size != BoundaryTypes.BASE_FRAME_SIZE:
            self.logger_util._log_print(f"Base Frame Length Incorrect,{response_frame_size} should be 4", color=Fore.RED, print_to_console=True,
                                        log=True, level=logging.ERROR)
            return False

        if response_frame[TargetIndices.SOF] != ProtocolConstants.SHELL_SOF.to_bytes(1, byteorder='little'):
            self.logger_util._log_print(f"SOF Value Not Correct Got {response_frame[TargetIndices.SOF]}, expected {TargetIndices.SOF}", color=Fore.RED, print_to_console=True,
                                        log=True, level=logging.ERROR)
            return False

        if response_frame[TargetIndices.KIND] != response_frame_kind.to_bytes(1, byteorder='little'):
            self.logger_util._log_print(f"Kind Value Not Correct Got {response_frame[TargetIndices.KIND]},expected {response_frame_kind}", 
                                        color=Fore.RED, print_to_console=True,
                                        log=True, level=logging.ERROR)
            return False

        return True

    def _receive_command(self, response_frame_kind: int) -> bytes:
        '''\
        receive command in expected format that complies with UART Shell.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.
        '''
        response_frame = []
        default_frame_responses = 4 + 1  # +1 for the NACK byte at the end
        is_partial_response_validated = False
        i = 0

        self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
        while i < default_frame_responses:
            byte_in_port = self.port.read(1)
            response_frame.append(byte_in_port)
            self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 

            # We want this to skip the second time it is validated, 
            # meaning we are at the end of the Frame
            if not is_partial_response_validated \
                and i == default_frame_responses - 2: # account for initial NACK offset

                is_pf_valid = self._validate_partial_frame(response_frame, response_frame_kind) 
                if is_pf_valid:
                    is_partial_response_validated = True
                    default_frame_responses += int.from_bytes(response_frame[TargetIndices.RECV_PAYLOAD_LEN], byteorder='little')
                else:
                    return StatusTypes.RECV_PARTIAL_FRAME_VALIDATION_ERROR
                
            i += 1

        self.logger_util._log_print(f"Recieved Command List {response_frame}",
                                    print_to_console=False, log=True, level=logging.INFO)

        return b''.join(response_frame)

    def _format_version_string(self, payload_bytes: bytes) -> str:
        payload_len = len(payload_bytes)
        return_str = ""
        for i in range(payload_len):
            return_str += str(payload_bytes[i])
            if i < payload_len-1:
                return_str += '.'
        return return_str
    
    def _format_response_number(self, payload_bytes: bytes) -> int:
        return int.from_bytes(payload_bytes, byteorder='little')

    def _isolate_target_indices(self, frame: bytes) -> tuple:
        '''\
        Isolate target parameters from the frame.
        '''
        payload_len = frame[TargetIndices.RECV_PAYLOAD_LEN]
        payload_end = TargetIndices.PAYLOAD_START + payload_len
        target_indices = [TargetIndices.PAYLOAD_START, payload_end] 
        
        return payload_len, payload_end, target_indices

    def get_version(self) -> str:
        version_command = self._construct_command(Kinds.GET_FIRMWARE_VERSION)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(version_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"Recieved Command Bytestr {frame}", print_to_console=False,
                                    log=True, level=logging.DEBUG)

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)  
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_version_string(frame[TargetIndices.PAYLOAD_START: payload_end])
