# -*- coding: utf-8 -*-
"""Administers the serial connection and communication protocol with the embedded MCUs.

This module contains the OnLogicM031Manager, used to  control and communicate with the 
Nuvoton microcontrollers embedded in OnLogic HX/K5xx products. 
"""

import time
import serial
import functools
import logging
import struct

from abc import ABC, abstractmethod
from serial.tools import list_ports as system_ports
from .command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices, BoundaryTypes
from fastcrc import crc8

logger = logging.getLogger(__name__)

class OnLogicM031Manager(ABC):
    """Administers the serial connection and communication protocol with the embedded MCUs.

    This class provides tools to communicate with the microcontrollers embedded in the
    K/HX-52x DIO-Add and Sequence MCU for Automotive Control. It contains the root
    context manager, serial handling methods, input validation, command construction,
    and frame reception and validation functionality. These are all inheritable by
    the child classes:
        * :class:`AutomotiveHandler`
        * :class:`DioHandler`

    Note:
        This class should not be directly called. Instead, it should be accessed through child classes like
        :class:`AutomotiveHandler` or :class:`DioHandler`.

        When using a child class as a context manager, the ``__enter__`` and ``__exit__``
        methods are called to claim and release the serial port. This means that the
        `serial_connection_label` should be specified as a parameter during the
        instantiation of the child class.

        The class and its children also contain extensive logging for debugging and
        tracking purposes. Logging is designed to trace the execution of the code and
        log important events, not the target payloads themselves (which are returned
        by called functions in child classes).         

        https://fastcrc.readthedocs.io/en/latest/ contains more info on the CRC8 methodology used.

    Example:
        Instantiating and using a child class (e.g., ``AutomotiveHandler``)
        with context manager:

        >>> with AutomotiveHandler(serial_connection_label="/dev/ttyS4") as my_auto:
        ...     # Perform operations with my_auto
        ...     pass

        Or using ``DioHandler``:

        >>> with DioHandler(serial_connection_label="/dev/ttyS5") as my_dio:
        ...     # Perform operations with my_dio
        ...     pass

    Args:
        serial_connection_label (str): The label or device path for the serial
            connection (e.g., "/dev/ttyS4"). This is passed when a child class
            is instantiated.

    Attributes:
        serial_connection_label (str): Stores the label for the serial connection.

        port (serial.Serial | None): The serial port object for communication,
            which is an instance of ``serial.Serial`` from the `pyserial` library
            once the port is opened, or None if not yet opened/set up.

        is_setup (bool): Indicates if the serial connection has been successfully
            set up (True) or not (False).
    """
    def __init__(self, serial_connection_label: str = None):
        """Initialize the OnLogicM031Manager class.
        
        Args:
            serial_connection_label (str): The label or device path for the serial
                connection (e.g., "/dev/ttySx" or ). This is passed when a child class
                is instantiated.
        """
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
        '''String representation of class.'''
        # TODO: Add FW version?
        repr_str = (
            f"Port: {self.serial_connection_label}\n"
            #f"FW Version\n"
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

    def list_all_available_ports(self, verbose: bool = False) -> None:
        """List all available serial ports.

        A convenient method provided to list all available serial ports on the system.
        The user should be able to the DIO card by it's Identifier if plugged in, but 
        unfortunately, the device descriptor is not available for the Sequence MCU for
        Automotive control. It is inheritable from the base class and can be called from
        both the Automotive and DIO classes.

        Args:
            verbose (bool): If True, prints detailed information about each port.
                            If False, prints only the port names.

        Returns:
            None: This method does not return anything. It prints the available ports to the console.        
        """
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
        """Scan and return the port of the target device.

        This method scans all available serial ports and returns the port of the target device
        based on the provided device ID and location. It is used to find the DIO card in the system.

        Args:
            dev_id (str): The device ID to search for.
            location (str): The location of the device. If None, it will not filter by location.

        Returns:
            str | None: The port of the target device if found, otherwise None.

        Note:
            For printable, user facing version of this method, see list_all_available_ports.
            It is inherited from the base class and can be called from both the Automotive and DIO classes.
        """
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
    def show_info(self) -> None:
        """Show information about the target MCU depending on the child class.

        This method is used to display information about the target MCU.
        It is an inheritable method provided to the base class. It will print a manual 
        to the console, which is a text file with the documentation of the target MCU.
        It closely interacts with the _read_files method, which is also an inheritable method.

        Args:
            None
        
        Returns:
            None
        
        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.
            Exception: For any other exceptions that may occur.
        """
        pass

    @abstractmethod
    def _init_port(self) -> serial.Serial:
        """Initialize the serial port with the given baudrate and device descriptor.

        If the port is not specified, it will search for the device with the 
        given VID and PID when used for DIO Utility. Otherwise, it will simply initialize
        the port with the given serial connection label. 

        If the port is not found, it will raise a ValueError.

        Args:
            None

        Returns:
            serial.Serial: The initialized serial port object.

            
        Raises:
            ValueError: If the port is not found or cannot be opened.
            serial.SerialException: If the port cannot be opened or configured.
            serial.SerialTimeoutException: If the port cannot be opened within the timeout period.

        Note: Each child class has a different implementation of this method.
        """
        pass

    @abstractmethod
    def _mcu_connection_check(self) -> None:
        """Check state of MCU.

        If MCU returns '\a' successively
        within a proper time interval, the correct port is found. 
        If not, the port is not correct or the MCU is not connected.
        It is an inheritable method provided to the base class.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If an the aknowledgement pattern is not received in the
            expected time and order. On failure it will list all available ports.
        """
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
                byte_in_port = self.port.read(1)
                if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_NACK:
                    logging.debug(f"{byte_in_port}")
                    nack_count += 1
                    self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(ProtocolConstants.STANDARD_DELAY)

        # If the number of nacks received is equal to the expected number of nacks
        # a potential interface is found, return
        if nack_count == ProtocolConstants.NACKS_NEEDED:
            logger.info("Interface Found")
            return

        logger.error(f"ERROR | AKNOWLEDGEMENT ERROR: " \
                     f"mismatch in number of nacks, check if {self.serial_connection_label} " \
                     f"is the right port?")

        self.list_all_available_ports()

        raise ValueError("ERROR | AKNOWLEDGEMENT ERROR")

    def _read_files(self, filename = None) -> None:
        """Read a file and print to console.
        
        This method [presumably] reads the documentation file
        and prints the contents to fine, skipping the lines that 
        include .rst code blocks.

        Args:
            filename (str): The name of the file to be read. 
                            If None, it will not read any file.

        Returns:
            None
        
        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.
            Exception: For any other exceptions that may occur.
        """
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if '.. code-block' in line:
                        continue
                    print(line.strip())
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except IOError:
            print(f"Error reading file {filename}.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Finished reading file.")

    def _reset(self, nack_counter: int = ProtocolConstants.NUM_NACKS, reset_buffers: bool = True) -> None:
        """Reset following the LPMCU ACK-NACK pattern.
        
        This method is used to clear serial buffers of both the MCU serial port and the host port.
        It ensures the buffer is clear in the LPMCU protocol in order to avild partial frames 
        being parsed by the host MCU.

        Args:
            nack_counter (int): The number of NACKs to send to clear the buffer.
                                Default is ProtocolConstants.NUM_NACKS.
            reset_buffers (bool): If True, resets the input and output buffers of the port.
                                  Default is True.
        Returns:
            None
        Raises:
            RuntimeError: If the number of bytes sent exceeds 1024.
            serial.SerialException: If the serial connection is not set up.
        """

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

    def _validate_input_param(self, input_value, valid_input_range: tuple, input_type: type) -> None:
        """Validates the input parameters for the LPMCU operation

        This method checks if the input value is of the expected type and within the valid range.
        If the input value is not of the expected type or out of range, it raises a TypeError or ValueError.    
        It additionally has a clause to make sure that the serial port is set up before operation,
        to prevent any runtime errors.

        Args:
            input_value (int | float): The value to be validated.
            valid_input_range (tuple): A tuple specifying the valid range for the input value.
                                       Example: (0, 4) means valid values are 0, 1, 2, 3.
            input_type (type): The expected type of the input value. Example: int, float.
        
        Returns:
            None: Does not return anything, just raises exceptions if incompatability is detected.

        Raises:
            serial.SerialException: If the serial connection is not set up.
            TypeError: If the input value is not of the expected type.
            ValueError: If the input value is out of the valid range.
        """
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
        """Check the CRC of the received frame.

        This method calculates the CRC of the received frame and 
        compares it with the existing CRC in the frame.

        Args:
            frame (bytes): The frame received from the microcontroller.
        
        Returns:
            bool: True if the CRC is valid, False otherwise.
        """
        # Check the len of the frame and make sure it is at least the base frame size
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
        """ Check if the target index or indices in the return_frame are within the valid range.

        Args:
            return_frame (bytes): The frame received from the microcontroller.

            target_index (int | tuple): Specifies the index or range of indices in the return_frame to check.
                                        If int: A single index in the return_frame to validate.
                                        If tuple: A range of indices (start, stop) to validate. 
                                        The range is inclusive of start and exclusive of stop.        
            
            target_range (tuple): The range target indices to check within the frame.
        
        Returns:
            bool: False if index check fails, True if all indices are within the valid range.  
        """
        payload_indices_to_check = []

        if isinstance(target_index, int):
            payload_indices_to_check = [target_index]

        elif isinstance(target_index, tuple):
            payload_indices_to_check = list(range(target_index[0], target_index[1]))
            logger.debug(f"Indices to check {payload_indices_to_check}")            

        else:
            logging.error(f"Invalid target_index type: {type(target_index)} or length: {len(target_index)}")
            return False

        for payload_idx in payload_indices_to_check:
            if not (target_range[0] <= return_frame[payload_idx] <= target_range[1]):
                return False

        return True

    def _validate_recieved_frame(self, return_frame: list, target_index: int | tuple = None, target_range: tuple = None) -> int:
        """Validate the received frame from the microcontroller.

        Checks for SOF, NACK, CRC and if the target index is within the valid range.
        If the target index is not provided, it will not check for the target range.
        Returns StatusTypes.SUCCESS if the frame is valid, otherwise returns the appropriate error code.
        
        Args:
            return_frame (list): The frame received from the microcontroller.
            target_index (int | tuple): Specifies the index or range of indices in the return_frame to check.
                                        If int: A single index in the return_frame to validate.
                                        If tuple: A range of indices (start, stop) to validate.
                                        The range is inclusive of start and exclusive of stop.
                                        Example: (0, 4) means valid values are 0, 1, 2, 3.
            target_range (tuple): The range of valid values for the target index.
                                        The range is inclusive of the first value and exclusive of the second value.
                                        Example: (0, 4) means valid values are 0, 1, 2, 3.
        
        Returns:
            int: Status code indicating the result of the validation.
                - StatusTypes.SUCCESS: Frame is valid.
                - StatusTypes.RECV_FRAME_VALUE_ERROR: Frame is None, not a list, or too short.
                - StatusTypes.RECV_FRAME_SOF_ERROR: SOF value is not correct.
                - StatusTypes.RECV_FRAME_NACK_ERROR: NACK not found in desired index.
                - StatusTypes.RECV_FRAME_CRC_ERROR: CRC check failed.
                - StatusTypes.RECV_UNEXPECTED_PAYLOAD_ERROR: Value(s) at idx not in target range.
        
        Raises:
            None: Designed specifically to not end and return an error code if the frame is not valid.
        """
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
        """ Validates partial frame recieved from microcontroller, it's used in the recieve_command method.

        Validate the partial frame (first four bytes) received from the MCU being used.
        This method is important as it ensures whether we can use the len field
        to determine the length of the payload that follows.

        Args:
            response_frame (list): The frame received from the microcontroller.
            response_frame_kind (int): The kind of the response frame.
        
        Returns:
            bool: True if the SOF, Kind field and len of the partial frame are valid. False otherwise.
        """

        # make sure that the partial frame is indeed a partial frame with 4 bytes
        response_frame_size = len(response_frame)
        if response_frame_size != BoundaryTypes.BASE_FRAME_SIZE:
            logger.error(f"Base Frame Length Incorrect,{response_frame_size} should be 4")
            return False

        # Check if the SOF is indeed 0x01
        if response_frame[TargetIndices.SOF] != ProtocolConstants.SHELL_SOF.to_bytes(1, byteorder='little'):
            logger.error(f"SOF Value Not Correct, Got {response_frame[TargetIndices.SOF]}, expected {TargetIndices.SOF}")
            return False

        # Make sure that the Kinds between the response frame and the type of message sent is correct.
        if response_frame[TargetIndices.KIND] != response_frame_kind.to_bytes(1, byteorder='little'):
            logger.error(f"Kind Value Not Correct, Got {response_frame[TargetIndices.KIND]}, expected {response_frame_kind}")
            return False

        return True

    def claim(self, serial_connection_label=None) -> None:
        """Claim the serial port and set up the connection.

        This method initializes the serial port with the given baudrate and device descriptor.
        If the port is not specified, it will search for the device with the given VID and PID when used for DIO Utility.
        Otherwise, it will simply initialize the port with the given serial connection label.

        Args:
            serial_connection_label (str): The label or device path for the serial
                connection (e.g., "/dev/ttySx" or "COMx"). This is passed when a child class
                is instantiated.
        
        Returns:
            None
        
        Raises:
            serial.SerialException: If the port cannot be opened or configured.
            ValueError: If the port is not found or cannot be opened.
        """

        if serial_connection_label is not None:
            self.serial_connection_label = serial_connection_label

        self.port = self._init_port()
        self._mcu_connection_check()
        self.is_setup = True
        self._reset() 
        logging.info("Serial Port Claimed")

    def release(self):
        """Release the serial port, reset the buffers, and reset the connection."""
        if self.is_setup:
            self._reset()
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            self.port.close()
            self.is_setup = False
            logging.info("Serial Port Successfully Released")

    @functools.lru_cache(maxsize=128)
    def _construct_command(self, kind: Kinds, *payload: int | bytes) -> bytes:
        """
        Construct a command to send to the Microcontroller, adhering to LPMCU protocol.
        
        This method constructs a bytes type command in the format of [SOF, CRC, LEN, KIND, PAYLOAD] 
        based on the command kind and payload. It is flexible and can handle differnt kinds of payloads,
        either a bytes type or a series of integers. The CRC is calculated using the smbus protocol 
        in thefastcrc library.

        More info on the ``Kinds`` type can be found in the command_set.py file.
        
        The method is decorated with @functools.lru_cache to cache the results of the function to prevent
        reconstructing the same command after the first construction.

        Args:
            kind (Kinds): The kind of command to construct.
            *payload (int | bytes): The payload to include in the command.
                                    It can be a series of integers or a bytes type payload.
            
        Returns:
            bytes: The constructed command in the format of [SOF, CRC, LEN, KIND, PAYLOAD].
        """
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
        """Send a command to the microcontroller byte-by-byte and validate the response.
        
        The return condition is that the ack count matches the length of the sent command,
        confirming that the mcu received every part of the command frame successfully. If not, it returns False.
        
        Args:
            command_to_send (bytes): The command to send to the microcontroller.
        
        Returns:
            bool: True if the command was sent successfully and acknowledged by the microcontroller.
                  False if there was a mismatch in the number of acknowledgements received.
        """

        # send command byte by byte and validate response
        logger.debug(f"Length of Command to send: {len(command_to_send)}")
        shell_ack_cnt = 0
        for byte in command_to_send:
            byte_to_send = byte.to_bytes(1, byteorder='little')

            logger.debug(f"Sending {byte} | {byte_to_send}")
            
            # self.port.write(byte.to_bytes(1, byteorder='little'))
            self.port.write(byte_to_send)
            byte_in_port = self.port.read(1)

            if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_ACK:
                shell_ack_cnt += 1

        if shell_ack_cnt == len(command_to_send):
            return True 

        logging.error(f"ERROR | AKNOWLEDGEMENT ERROR mismatch in number of acknowledgements, reduce access speed?")

        return False

    def _receive_command(self, response_frame_kind: int) -> bytes | int:
        """Recieves pertinent response frames from the microcontroller.

        Receive command in expected format that complies with UART Shell interface.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.

        Args:
            response_frame_kind (int): The kind of the response frame to expect.
                                       It is used to validate the response frame.
                                       Refer to the ```Kinds``` enum in command_set.py for more info.

        Returns:
            bytes: The received command as a bytes object if the response is valid.
                   If the response is not valid, it returns an error code from StatusTypes.

        Raises:
            StatusTypes.RECV_UNEXPECTED_PAYLOAD_ERROR: If the payload length is not as expected.
            StatusTypes.RECV_PARTIAL_FRAME_VALIDATION_ERROR: If the partial frame validation fails.
        """
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
        """Format bytes type payload to a string representation.

        Format the payload byte to a string representation in the format Byte1.Byte2.Byte3, 
        where each byte is a converted byte value to string

        Example: b'\x01\x02\x03' -> '1.2.3'

        Args:
            payload_bytes (bytes): The payload bytes to be formatted.
        
        Returns:
            str: The formatted string representation of the payload bytes.
        """
        payload_len = len(payload_bytes)
        return_str = ""
        for i in range(payload_len):
            return_str += str(payload_bytes[i])
            if i < payload_len - 1: 
                return_str += '.'
        return return_str
    
    def _format_response_number(self, payload_bytes: bytes, format_type: type = int) -> int:
        """Simple shorthand method to format the payload bytes to an integer representation.

        A simple method that formats the payload bytes to an integer representation with an additional None check.
        Example: b'\x00\x00\x00\x01' -> 1
        If the payload is empty, it returns StatusTypes.FORMAT_NONE_ERROR.
        
        Args:
            payload_bytes (bytes): The payload bytes to be formatted.
        
        Returns:
            int: The formatted integer value of the payload bytes.
                 If the payload is empty, it returns StatusTypes.FORMAT_NONE_ERROR.
        """
        ret_val = StatusTypes.FORMAT_NONE_ERROR

        if payload_bytes:
            if format_type == int:
                ret_val = int.from_bytes(payload_bytes, byteorder='little')  
            elif format_type == float:
                # Will return a tuple with the remaining values in a buffer,
                # need to get the first value from the tuple
                ret_val = struct.unpack('<f', payload_bytes)[0]

        return ret_val

    def _isolate_target_indices(self, frame: bytes) -> tuple:
        """Isolate target indices from the frame. 
        
        It operates on the assumption that 
        1) input is a bytes object type and 2) there is at least 1 payload value indicated
        by the len field of the returned frame.
        
        ATTENTION: The payload_end value is exclusive to follow Python list slicing.
        The start index is inclusive, while the end index is exclusive.
        This means that the target indices are from start to end-1.

        Args:
            frame (bytes): The formetted bytestring frame received from microcontroller
        
        Returns:
            payload_len (int): The length of the payload
            payload_end (int): The end index of the payload + 1.
            target_indices (tuple[int, int]): A tuple containing the start and end indices of the payload. The end value is excusive to align with Python's 
                                              list slicing and range functions. So, it's beginning to end-1 as the actual target indices.
        """
        payload_len = frame[TargetIndices.RECV_PAYLOAD_LEN]
        payload_end = TargetIndices.PAYLOAD_START + payload_len
        target_indices = (TargetIndices.PAYLOAD_START, payload_end)
        
        return payload_len, payload_end, target_indices

    def get_version(self) -> str | int:
        """Get the firmware version of the microcontroller.
        
        Retrieves the firmware of the microcontroller by using the GET_FIRMWARE_VERSION command
        and the LPMCU protocol discussed in the documentation and README. 
        The version is returned as a string in the format "X.X.X",
        
        Params:
            None

        Returns:
            str: The firmware version of the microcontroller in the format "X.X.X".
                  If the version cannot be retrieved, it returns StatusTypes.SEND_CMD_FAILURE.
                  If the payload is empty, it returns StatusTypes.FORMAT_NONE_ERROR.
        """
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
