# -*- coding: utf-8 -*-
"""DioHandler module for managing Digital Input/Output (DIO) operations.

Provides methods that allow users to access nearly all features of DIO card. 
"""

import time
import serial
import logging
from .onlogic_nuvoton_manager import OnLogicNuvotonManager
from .command_set import TargetIndices, ProtocolConstants, Kinds, StatusTypes, BoundaryTypes

logger = logging.getLogger(__name__)

class DioHandler(OnLogicNuvotonManager):
    """Handles Digital Input/Output (DIO) operations for the DIO card.
    
    This class provides methods to get and set the states of digital input and output pins.
    It can get and set input and output pins individually, or in bulk. It uses the LPMCU methods
    and protocolls, inherited from OnLogicNuvotonManager. A new feature in this
    line of DIO cards is the ability to set the contact type of the pins to Wet or Dry.

    As a reminder, the DIO card has 8 digital input pins and 8 digital output pins.
    The digital input pins are active-low, meaning that a 0 indicates that the pin is on,
    and a 1 indicates that the pin is off. The digital output pins are active-high, meaning
    that a 0 indicates that the pin is off, and a 1 indicates that the pin is on.
    The DIO card also has a contact type for each pin, which can be either Wet or Dry.
    The contact type is set using the set_di_contact and set_do_contact methods.
    The contact type can be gotten by using the get_di_contact and get_do_contact methods.
    
    The claim method is used to connect to the DIO card and the parameter can be left blank 
    for an auto-lock onto the port. The release method disconnects from the DIO card.
    
    Note:
        More information on the DIO card can be found in the Data sheet, and also by calling the
        show_info method.

    Pin Diagram:
        ---------------------------------------------------------------
        ||  _     _     _     _     _     _     _     _     _     _  ||
        || |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Input
        || INT | DI7 | DI6 | DI5 | DI4 | DI3 | DI2 | DI1 | DI0 |  -  ||
        ---------------------------------------------------------------
        ||  _     _     _     _     _     _     _     _     _     _  ||
        || |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_|   |_| || Digital Output
        || GND | DO7 | DO6 | DO5 | DO4 | DO3 | DO2 | DO1 | DO0 |  +  ||
        ---------------------------------------------------------------

    Attributes:
        serial_connection_label (str): The label of the serial connection.
            If None, the class will attempt to find the correct port automatically.
    
    Examples:
        Claim and release port for the DioHandler class with either:

        my_dio = DioHandler() 
        my_dio.claim()
        ...
        my_dio.release()

        or

        with DioHandler() as dio_handler:
            ...
    """
    def __init__(self, serial_connection_label: str = None):
        """Initializes the DioHandler class.
        
        Args:
            serial_connection_label (str): The label of the serial connection.
                If None, the class will attempt to find the correct port automatically.
        """
        super().__init__(
                          serial_connection_label=serial_connection_label
                        )

    def _init_port(self) -> None:
        '''Init port and establish USB-UART connection.'''
        if self.serial_connection_label is None:
            self.serial_connection_label = self._get_cdc_device_port(ProtocolConstants.DIO_MCU_VID_PID_CDC, ".0")

        try:
            if self.serial_connection_label is not None:
                return serial.Serial(self.serial_connection_label, ProtocolConstants.BAUDRATE, timeout=1)
            else:
                type_connect_error = f"ERROR | USB CDC not found, is the DIO card configured right?"
                logger.error(type_connect_error)
                raise TypeError(type_connect_error)

        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?"
            logger.error(serial_connect_err)
            self.serial_connection_label = None # Revisit if is worth setting up like this
            raise serial.SerialException(serial_connect_err)

    def _mcu_connection_check(self) -> None:
        """Inherited method from OnLogicNuvotonManager to check if the DIO card is connected."""
        super()._mcu_connection_check()

        # TODO: issue specific command to see if the DIO card is connected
        # if self.get_di(0) not in BoundaryTypes.BINARY_VALUE_RANGE:
        #    raise ValueError("Error | Incorrect Value returned, is this the right device?")

    def show_info(self) -> None:
        """Displays DIO card info located in the docs folder, required OnLogicNuvotonManager."""
        relative_path = '../docs/ShowInfo/DioHandlerDescription.rst'
        super()._read_files(filename=relative_path)

    def get_di(self, di_pin: int) -> int:
        """Gets the state of active-low digital inputs on the DIO card.

        Args:
            di_pin (int): digital input pin with range [0-7]
        
        Returns:
            int: 0, indicating on, 1, indicating off,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.
        
        Raises:
            ValueError: if di_pin is not in the range of 0-7
            TypeError: if di_pin is not an integer

        Example:
            >>> with DioHandler() as dio_handler:
            ...     dio_handler.get_di(0)
            1
        """
        self._validate_input_param(di_pin, BoundaryTypes.DIGITAL_IO_PIN_RANGE, int)

        di_command = self._construct_command(Kinds.GET_DI, di_pin)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        
        if not self._send_command(di_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DI)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        # Retrieve do value located in penultimate idx of frame
        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def get_do(self, do_pin: int) -> int:
        """Gets the state of active-high digital outputs on the DIO card.

        Args:
            do_pin (int): digital output pin with range [0-7]

        Returns:
            int: 0, indicating off, 1, indicating on,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.

        Raises:
            ValueError: if do_pin is not in the range of 0-7
            TypeError: if do_pin is not an integer

        Example:
            >>> with DioHandler() as dio_handler:
            ...     dio_handler.get_do(0)
            1
        """
        self._validate_input_param(do_pin, BoundaryTypes.DIGITAL_IO_PIN_RANGE, int)

        do_command = self._construct_command(Kinds.GET_DO, do_pin)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DO)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        # Retrieve do value located in penultimate idx of frame
        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_do(self, pin: int, value: int) -> int:
        """Sets the state of active-high digital outputs on the DIO card.

        Args:
            pin (int): digital output pin with range [0-7]
            value (int): binary value to set the pin to, either 0 or 1
        Returns:
            int: 0, indicating success,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.

        Raises:
            ValueError: if pin is not in the range of 0-7
            TypeError: if pin or value is not an integer

        Example:
            >>> with DioHandler() as dio_handler:
            ...     dio_handler.set_do(0, 1)
            0
        """
        self._validate_input_param(pin, BoundaryTypes.DIGITAL_IO_PIN_RANGE, int)
        self._validate_input_param(value, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_do_command = self._construct_command(Kinds.SET_DO, pin, value)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_DO)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def get_di_contact(self) -> int:
        """Gets the contact state of the digital input pins on the DIO card.

        0 indicates that DI is in Wet Contact mode and 1 Indicates that DI is in Dry Contact Mode.
        
        Args:
            None
        
        
        Returns:
            int: 0, indicating Wet Contact, 1, indicating Dry Contact,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.
        Raises:
            TypeError: if contact_type is not an integer
            ValueError: if contact_type is not in the range of 0-1
        
        Note:
            Consult DIO description section of the data sheet for more details on 
            the specification of contact types.

        Example:
            >>> with DioHandler() as dio_handler:
            ...     dio_handler.get_di_contact()
            0
        """
         
        di_contact_state_cmd = self._construct_command(Kinds.GET_DI_CONTACT)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DI_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False) 
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def get_do_contact(self) -> int:
        """Gets the contact state of the digital output pins on the DIO card.
        
        0 indicates that DO is in Wet Contact mode and 1 Indicates that DO is in Dry Contact Mode.
        
        Args:
            None
        
        Returns:
            int: 0, indicating Wet Contact, 1, indicating Dry Contact,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.
        
        Raises:
            TypeError: if contact_type is not an integer
            ValueError: if contact_type is not in the range of 0-1
        
        Note:
            Consult DIO description section of the data sheet for more details on 
            the specification of contact types.
        
        Example:
            >>> with DioHandler() as dio_handler:
            ...     dio_handler.get_do_contact()
            0
        """

        do_contact_state_cmd = self._construct_command(Kinds.GET_DO_CONTACT)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(do_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DO_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_di_contact(self, contact_type: int) -> int:
        """Sets the contact state of the digital input pins on the DIO card.
        
        0 indicates that DI is in Wet Contact mode and 1 Indicates that DI is in Dry Contact Mode.

        Args:
            contact_type (int): 0 for Wet Contact, 1 for Dry Contact

        Returns:
            int: 0, indicating success,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.

        Raises:
            TypeError: if contact_type is not an integer
            ValueError: if contact_type is not in the range of 0-1

        Note:
            Consult DIO description section of the data sheet for more details on 
            the specification of contact types.
        """
        self._validate_input_param(contact_type, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_di_contact_state_cmd = self._construct_command(Kinds.SET_DI_CONTACT, contact_type)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
    
        if not self._send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_DI_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def set_do_contact(self, contact_type: int) -> int:
        """Sets the contact state of the digital output pins on the DIO card.

        0 indicates that DO is in Wet Contact mode and 1 Indicates that DO is in Dry Contact Mode.
        
        Args:
            contact_type (int): 0 for Wet Contact, 1 for Dry Contact
        
        Returns:
            int: 0, indicating success,
                 StatusTypes.SEND_CMD_FAILURE if command send failed,
                 or any other negative value indicating failure.
        
        Raises:
            TypeError: if contact_type is not an integer
            ValueError: if contact_type is not in the range of 0-1
        
        Note:
            Consult DIO description section of the data sheet for more details on 
            the specification of contact types.
        """
        self._validate_input_param(contact_type, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_di_contact_state_cmd = self._construct_command(Kinds.SET_DO_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_DO_CONTACT)
        if not isinstance(frame, bytes):
            return frame
        
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def get_all_input_states(self) -> list:
        '''
        all_input_states = []
        
        for i in range(0, 8):
            all_input_states.append()

        return all_input_states
        '''
        DI_PIN_MIN, DI_PIN_MAX = BoundaryTypes.DIGITAL_IO_PIN_RANGE
        return [self.get_di(state) for state in range(DI_PIN_MIN, DI_PIN_MAX + 1)]


    def get_all_output_states(self) -> list:
        """Gets the states of all digital output pins.
        
        This is a wrapper method that calls get_do for each pin in the range of 0-7.
        The method returns a list of 8 binary values, one for each output pin.
        Indices 0-7 correspond to output pins 0-7 respectively.

        Args:
            None
        
        Returns:
            list[int]: A list of 8 binary-valued pin states, if successful, all values should be between 0 and 1. 
                        values < 0 indicate failure.
        """
        DO_PIN_MIN, DO_PIN_MAX = BoundaryTypes.DIGITAL_IO_PIN_RANGE
        return [self.get_do(state) for state in range(DO_PIN_MIN, DO_PIN_MAX + 1)]

    def get_all_io_states(self) -> list:
        return [self.get_all_input_states(), self.get_all_output_states()]

    def set_all_output_states(self, do_lst: list) -> list:
        """Sets the states of all digital output pins given an input list of binary inputs.

        This is a wrapper method that calls set_do for each pin in the range of 0-7.
        Sets the states of all digital output pins given an input list of binary inputs.
        Indices 0-7 correspond to output pins 0-7 respectively.
        
        Args:
            do_lst (list[int]): A list of 8 values (0 or 1), one for each output pin.
            
        Returns:
            list[int]: A list of status codes for each pin operation, there should be 7 in total. 
                       0 indicates success; < 0 indicates failure.
        
        Raises:
            TypeError: If do_lst is not a list or is None.
            ValueError: If do_lst does not contain exactly 8 values or contains invalid values, i.e.
                        if any value in do_lst is not a binary valued integer in the range of 0-1.
        """
        _, DO_PIN_MAX = BoundaryTypes.DIGITAL_IO_PIN_RANGE

        if not isinstance(do_lst, list):
            do_list_type_err = "ERROR | do_list must be a list of 8 values, one for each available output pin"
            logger.error(do_list_type_err)
            raise TypeError(do_list_type_err)

        if len(do_lst) != DO_PIN_MAX + 1:
            do_list_len_err = "ERROR | do_list must contain exactly 8 values, one for each available output pin" 
            logger.error(do_list_len_err)
            raise ValueError(do_list_len_err)

        for do in do_lst:
            self._validate_input_param(do, BoundaryTypes.BINARY_VALUE_RANGE, int)

        return [self.set_do(do_lst_idx, do_lst_val) for do_lst_idx, do_lst_val in enumerate(do_lst)]
