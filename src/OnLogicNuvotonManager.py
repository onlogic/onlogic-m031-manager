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
import logging

from abc import ABC, abstractmethod
from serial.tools import list_ports as system_ports
from command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices, BoundaryTypes
from fastcrc import crc8

logger = logging.getLogger(__name__)

class OnLogicNuvotonManager(ABC):
    '''
    Administers the serial connection with the
    microcontroller embedded in the K/HX-52x DIO-Add and Sequence MCU for Automotive Control.
    '''
    def __init__(self, serial_connection_label: str = None):
        '''Init class by establishing serial connection.''' 
        # Setup mechanism so deleter does not delete non-existant objects
        self.is_setup = False
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
            #f"FW Version: {self.get_version()}\n"
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

    def list_all_available_ports(self, verbose: bool = False):
        all_ports = system_ports.comports()
        for port in sorted(all_ports):
            if not verbose:
                print(port)
                logging.info(port)
            elif verbose:
                comport_info = (
                        f"Port: {port}\n"
                        f"Port Location: {port.location}\n"
                        f"Hardware ID: {port.hwid}\n"
                        f"Device: {port.device}\n"
                 )
                print(comport_info)
                logging.info(comport_info)  

    def _get_cdc_device_port(self, dev_id: str, location: str = None) -> str | None:
        """Scan and return the port of the target device."""
        all_ports = system_ports.comports() 
        for port in sorted(all_ports):
            if dev_id in port.hwid:
                if location and location in port.location:
                    logging.info(f"NOTE | DIO CARD FOUND ON:\n"
                                f"Port: {port}\n"
                                f"Port Location: {port.location}\n"
                                f"Hardware ID: {port.hwid}\n"
                                f"Device: {port.device}",
                                )
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
                    logging.debug(f"{byte_in_port}")
                    nack_count += 1
                    self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(ProtocolConstants.STANDARD_DELAY)

        if nack_count == ProtocolConstants.NACKS_NEEDED:
            logger.info("Interface Found")
            return

        logger.error(f"ERROR | AKNOWLEDGEMENT ERROR: " \
                     f"mismatch in number of nacks, check if {self.serial_connection_label} " \
                     f"is the right port?")

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
                
                logging.error(ack_error_msg)
                
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

    def _validate_input_param(self, input_value, valid_input_range: tuple, input_type: type):
        if self.is_setup is False:
            raise serial.SerialException("ERROR | Serial Connection is not set up, did you claim the port?")

        if type(input_value) != input_type:
            type_error_msg = f"ERROR | {type(input_value)} was found when {input_type} was expected"

            logging.error(type_error_msg)

            raise TypeError(type_error_msg)

        if input_value < valid_input_range[0] \
                or input_value > valid_input_range[1]:
            value_error_msg = "ERROR | Out of Range Value Provided: " + str(input_value) + "." + \
                              " Valid Range " + str(valid_input_range)

            logging.error(value_error_msg)

            raise ValueError(value_error_msg)

    def _check_crc(self, frame: bytes) -> bool:
        if len(frame) < BoundaryTypes.BASE_FRAME_SIZE:
            return False

        # add 1 make penultimate index the last value in slice
        crc_bytes = frame[TargetIndices.RECV_PAYLOAD_LEN: TargetIndices.PENULTIMATE+1] 
        
        crc_val = crc8.smbus(crc_bytes)

        logging.debug(f"CALCULATED {crc_val} : EXISTING {frame[TargetIndices.CRC]}")

        if crc_val != frame[TargetIndices.CRC]:
            logging.debug(f"CRC MISMATCH")
            return False

        return True

    def _within_valid_range(self, return_frame: bytes, target_index: int | tuple, target_range: tuple) -> bool:        
        '''

        :target_index (int | tuple):
            Specifies the index or range of indices in the return_frame to check.
            If int: A single index in the return_frame to validate.
            If tuple: A range of indices (start, stop) to validate. The range is inclusive of start and exclusive of stop.        
        '''
        
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
        '''\
        Validate the received frame from the microcontroller.
        Checks for SOF, NACK, CRC and if the target index is within the valid range.
        If the target index is not provided, it will not check for the target range.
        Returns StatusTypes.SUCCESS if the frame is valid, otherwise returns the appropriate error code.
        '''
        if return_frame is None or isinstance(return_frame, list) \
              or len(return_frame) < BoundaryTypes.BASE_FRAME_SIZE:
            logging.error(f"Received Frame {return_frame} is None, not a list, or too short")
            return StatusTypes.RECV_FRAME_VALUE_ERROR
        
        if return_frame[TargetIndices.SOF] != ProtocolConstants.SHELL_SOF:
            logging.error(f"SOF Value Not Correct")
            return StatusTypes.RECV_FRAME_SOF_ERROR

        if return_frame[TargetIndices.NACK] != ProtocolConstants.SHELL_NACK:
            logging.error(f"NACK Not Found in Desired Index")
            return StatusTypes.RECV_FRAME_NACK_ERROR

        is_crc = self._check_crc(return_frame)
        if not is_crc:
            logging.error(f"CRC Check fail")
            return StatusTypes.RECV_FRAME_CRC_ERROR

        if target_index is not None \
                and not self._within_valid_range(return_frame, target_index, target_range): 
            
            logging.error(f"Value(s) at idx {target_index} not in target range: {target_range}")
            
            return StatusTypes.RECV_UNEXPECTED_PAYLOAD_ERROR

        logger.debug(f"Validated frame successfully: {return_frame}")
        return StatusTypes.SUCCESS

    def _validate_partial_frame(self, response_frame: list, response_frame_kind: int) -> bool:
        '''\
        Validate the partial frame (first four bytes) received from the MCU being used.
        This function is important as it ensures whether we can use the len field 
        to determine the length of the payload that follows.
        '''
        response_frame_size = len(response_frame)
        if response_frame_size != BoundaryTypes.BASE_FRAME_SIZE:
            logger.error(f"Base Frame Length Incorrect,{response_frame_size} should be 4")
            return False

        if response_frame[TargetIndices.SOF] != ProtocolConstants.SHELL_SOF.to_bytes(1, byteorder='little'):
            logger.error(f"SOF Value Not Correct, Got {response_frame[TargetIndices.SOF]}, expected {TargetIndices.SOF}")
            return False

        if response_frame[TargetIndices.KIND] != response_frame_kind.to_bytes(1, byteorder='little'):
            logger.error(f"Kind Value Not Correct, Got {response_frame[TargetIndices.KIND]},expected {response_frame_kind}")
            return False

        return True

    def claim(self, serial_connection_label=None) -> None:
        # Serial device functionality
        if serial_connection_label is not None:
            self.serial_connection_label = serial_connection_label

        self.port = self._init_port()
        self._mcu_connection_check()
        self.is_setup = True
        self._reset() 
        logging.info("Serial Port Claimed")

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
            logging.info("Serial Port Successfully Released")

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

        logging.info(f"Constructed Command {constructed_command}")
        
        return constructed_command

    def _send_command(self, command_to_send: bytes) -> bool:
        # send command byte by byte and validate response
        logger.debug(f"Length of Command to send: {len(command_to_send)}")
        shell_ack_cnt = 0
        for byte in command_to_send:
            logger.debug(f"Sending {byte}")
            self.port.write(byte.to_bytes(1, byteorder='little'))
            byte_in_port = self.port.read(1)

            if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_ACK:
                shell_ack_cnt += 1

        if shell_ack_cnt == len(command_to_send):
            return True 

        logging.error(f"ERROR | AKNOWLEDGEMENT ERROR mismatch in number of aknowledgements, reduce access speed?")

        return False

    def _receive_command(self, response_frame_kind: int) -> bytes | int:
        '''
        Receive command in expected format that complies with UART Shell interface.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.
        '''
        response_frame = []
        is_partial_response_validated = False
        
        max_byte_requests = 4 + 1  # +1 for the NACK byte at the end
        requests = 0

        self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
        while requests < max_byte_requests:
            
            byte_in_port = self.port.read(1)
            response_frame.append(byte_in_port)
            self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little')) 
            
            logger.debug(f"Received Byte: {byte_in_port}")

            # Validate partial frame
            if not is_partial_response_validated and requests == max_byte_requests - 2:
            
                logger.debug(f"Validating Partial Frame {response_frame}")

                is_pf_valid = self._validate_partial_frame(response_frame, response_frame_kind) 
                if is_pf_valid:
                    is_partial_response_validated = True

                    # Add payload length to determine remaining byte requests
                    try:
                        payload_length = int.from_bytes(response_frame[TargetIndices.RECV_PAYLOAD_LEN], byteorder='little')
                        max_byte_requests += payload_length
                    except (ValueError, IndexError) as e:
                        logger.error(f"Error parsing payload length: {e}")
                        return StatusTypes.RECV_UNEXPECTED_PAYLOAD_ERROR
                else:
                    logger.error("Partial frame validation failed.")
                    return StatusTypes.RECV_PARTIAL_FRAME_VALIDATION_ERROR

            requests += 1

        logger.info(f"Received Command List {response_frame}")

        return b''.join(response_frame)

    def _format_version_string(self, payload_bytes: bytes) -> str:
        '''\
            Format the payload byte to a string representation, 
            in the format Byte1.Byte2.Byte3, where each byte is a coverted byte value to string

            Example: b'\x01\x02\x03' -> '1.2.3'
        '''
        payload_len = len(payload_bytes)
        return_str = ""
        for i in range(payload_len):
            return_str += str(payload_bytes[i])
            if i < payload_len - 1: 
                return_str += '.'
        return return_str
    
    def _format_response_number(self, payload_bytes: bytes) -> int:
        '''\
            A simple method that formats the payload bytes to an integer representation with an additional None check.
            Example: b'\x00\x00\x00\x01' -> 1
            If the payload is empty, it returns StatusTypes.FORMAT_NONE_ERROR.
        '''

        return int.from_bytes(payload_bytes, byteorder='little') if payload_bytes else StatusTypes.FORMAT_NONE_ERROR

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

        frame = self._receive_command(Kinds.GET_FIRMWARE_VERSION)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)  
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_version_string(frame[TargetIndices.PAYLOAD_START: payload_end])
