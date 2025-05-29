# -*- coding: utf-8 -*-
"""Provides the AutomotiveHandler class for managing automotive features of the OnLogic Nuvoton MCU.

This module includes methods to interact with the automotive features of the OnLogic Nuvoton MCU.
For more information about the automotive mode settings, please refer to the Automotive section of the documentation or the
docstrings below.
"""

import time
import serial
import logging
from .onlogic_m031_manager import OnLogicM031Manager
from .command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices, BoundaryTypes

logger = logging.getLogger(__name__)

class AutomotiveHandler(OnLogicM031Manager):
    """AutomotiveHandler class for managing automotive features of the OnLogic Nuvoton MCU.

    This class provides methods to interact with the automotive features of the OnLogic Nuvoton MCU.
    For more information about the automotive features, please refer to the AutomotiveModeDescription section of
    the documentation or the docstrings below.

    K52x Ignition Pin Diagram:

    .. code-block:: text

        ---------------------------------
        ||  _     _     _     _     _  ||
        || |_|   |_|   |_|   |_|   |_| ||  
        || IGN |  +  |  +  |  -  |  -  ||  
        ---------------------------------

    Attributes:
        serial_connection_label (str): The label of the serial connection. 
    
    Examples:
        Claim and release port for the Automotive class with either:

        .. code-block:: python

            my_auto = AutomotiveHandler()

            # will be "/dev/ttySX" on Linux or "COMX" on Windows
            my_auto.claim("COMX")
            # ... (other operations)
            my_auto.release()

        or

        .. code-block:: python

            with AutomotiveHandler() as my_auto:
                # ... (operations within the context manager)
                # Port is claimed on entry and released on exit
                pass
    """
    def __init__(self, serial_connection_label = None):
        """Initialize the AutomotiveHandler class.
        
        Args:
            serial_connection_label (str): The label of the serial connection.
        """
        super().__init__(
                         serial_connection_label=serial_connection_label
                        )

    def _mcu_connection_check(self) -> None:
        """Check the connection to the MCU.

        If it returns '\a' successively within a proper time interval, 
        the correct port is found. If not, the port is not correct or the MCU is not connected.
        It is inherited from the OnLogicM031Manager class.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If an the aknowledgement pattern is not received in the
            expected time and order.
        """

        super()._mcu_connection_check()

        # TODO: Implement a more robust check to determine the MCU type
        # if(not self.get_soft_off_timer()):
        #     raise ValueError("Error | Issue with verifying connection command")
        
    def _init_port_error_handling(self, error_msg: str, return_early: bool = False) -> None | ValueError:
        """Light error handling assistance for the init port method."""
        logger.error(error_msg)
        self.list_all_available_ports()

        if return_early is True:
            return

        raise ValueError(error_msg)

    def _init_port(self) -> serial.Serial:
        """Init port and establish USB-UART connection.
        
        This is an internal method that initializes the serial port for communication on 
        the sequence microcontroller over UART. It checks if the port is provided and available,
        and then attempts to establish a serial connection. If the same serial port that the 
        DIO card is connected to is provided, an error is raised.

        Args:
            None

        Returns:
            serial.Serial: Serial connection object.

        Raises:
            ValueError: If the port is not provided or if the port is not available.
            SerialException: If the serial connection cannot be established.
        """
        if self.serial_connection_label is None:
            self._init_port_error_handling("ERROR | You must provide a PORT input string for Automotive Mode")
        elif (self.serial_connection_label == self._get_cdc_device_port(ProtocolConstants.DIO_MCU_VID_PID_CDC, ".0")):
            self._init_port_error_handling("Error | DIO COM Port Provided for automotive port entry")
        try:
            return serial.Serial(self.serial_connection_label, ProtocolConstants.BAUDRATE, timeout=1)
        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?" \
                                  "Did you enable correct bios settings []?"
            self._init_port_error_handling(serial_connect_err, return_early=True)
            raise serial.SerialException(serial_connect_err)

    def show_info(self) -> None:
        relative_path = '../docs/ShowInfo/AutomotiveModeDescription.rst'
        super()._read_files(filename=relative_path)

    def get_automotive_mode(self) -> int:
        """Get the automotive mode of the device.

        Automotive-mode enables or disables system automotive features,
        this method uses the LPMCU protocol discussed in the README and 
        documentation to get the automotive mode from the Sequence MCU.

        Args:
            None
        
        Returns:
            int: The automotive mode of the device. 0 indicates that the device is not in automotive mode,
                1 indicates that the device is in automotive mode.

                A value < 0 indicates an error in the command or response.    
        Example:
            >>> auto_mode = get_automotive_mode()
            >>> print(f"Automotive Mode: {auto_mode}")
            Automotive Mode: 1
        """
        amd = self._construct_command(Kinds.GET_AUTOMOTIVE_MODE)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(amd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_AUTOMOTIVE_MODE)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False) 
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]
    
    def set_automotive_mode(self, amd: int) -> int:
        """Set the automotive mode of the device.
        
        Automotive-mode enables or disables system automotive features. This method uses the
        LPMCU protocol discussed in the README and documentation to set the set whether the device 
        is in automotive mode or not.
        
        Args:
            amd (int): The automotive mode to set. 0 turn automotive mode off, 1 turn automotive mode on.
        
        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.
        
        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.
        
        Example:
            >>> auto_mode = my_auto.set_automotive_mode(1)
            >>> print(f"Automotive Mode Set to: {auto_mode}")
            Automotive Mode Set to: 0
        """
        self._validate_input_param(amd, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_auto_mode = self._construct_command(Kinds.SET_AUTOMOTIVE_MODE, amd)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_auto_mode):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_AUTOMOTIVE_MODE)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def get_low_power_enable(self) -> int:
        """Get the low power enable status value from the MCU.

        Low Power Enable enables entering a very low power state when the system powers off. 
        The system can only wake from the power-button and the ignition switch 
        when in this power state.This method uses the LPMCU protocol discussed in the README 
        and documentation to get the low power enable status from the Sequence MCU.
        
        Args:
            None
        
        Returns:
            int: The low power enable status of the device. 0 indicates that low power mode is disabled,
                1 indicates that low power mode is enabled.
                A value < 0 indicates an error in the command or response.
        
        Example:
            >>> low_power_enable = my_auto.get_low_power_enable()
            >>> print(f"Low Power Enable: {low_power_enable}")
            Low Power Enable: 1
        """
        lpe_command = self._construct_command(Kinds.GET_LOW_POWER_ENABLE)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(lpe_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_LOW_POWER_ENABLE)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False) 
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_low_power_enable(self, lpe: int) -> int:
        """Set the low power enable status in the sequence MCU.

        Low Power Enable enables entering a very low power state when the system powers off. 
        The system can only wake from the power-button and the ignition switch when in this power state.
        This method uses the LPMCU protocol discussed in the README and documentation to set the low power 
        enable status of the sequence MCU.
        
        Args:
            lpe (int): The low power enable status to set. 0 turn low power mode off, 1 turn low power mode on.
        
        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.
        
        Example:
            >>> status = my_auto.set_low_power_enable(1)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """
        self._validate_input_param(lpe, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_lpe_cmd = self._construct_command(Kinds.SET_LOW_POWER_ENABLE, lpe)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_lpe_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_LOW_POWER_ENABLE) 
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        
    def get_start_up_timer(self) -> int:
        """Get the start-up timer value from the MCU.

        The start-up timer controls the number of seconds that the 
        ignition input must be stable before the system will power on.
        This method uses the LPMCU protocol discussed in the README and documentation
        to get the start up timer.

        Args:
            None

        Returns:
            int: the start-up timer value of the device in seconds.  
                 the start-up timer can be configured between 1 - 1048575 seconds
                 A value < 0 indicates an error in the command or response.
        Example:
            >>> start_up_timer = my_auto.get_start_up_timer()
            >>> print(f"Start Up Timer: {start_up_timer}")
            Start Up Timer: 10
        """
        sut_cmd = self._construct_command(Kinds.GET_START_UP_TIMER)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(sut_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_START_UP_TIMER)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START: payload_end])

    def set_start_up_timer(self, sut: int) -> int:
        """Set the start-up timer value in the sequence MCU.
        
        The start-up timer controls the number of seconds that the ignition input
        must be stable before the system will power on. This method uses the LPMCU 
        protocol discussed in the README and documentation to set the start up timer 
        of the sequence MCU.
        
        Args:
            sut (int): The start up timer to set. 1 - 1048575 seconds.

        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.

        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.

        Example:
            >>> status = my_auto.set_start_up_timer(10)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """ 
        self._validate_input_param(sut, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int) 

        set_sut_cmd = self._construct_command(Kinds.SET_START_UP_TIMER, sut.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_sut_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_START_UP_TIMER) 
        if not isinstance(frame, bytes):
            return frame

        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)

    def get_soft_off_timer(self) -> int:
        """Get the existing soft-off timer value from the MCU.

        The soft-off timer controls the number of seconds that the ignition input
        can be low before the mcu requests the system powers down via a virtual 
        power button event. This method uses the LPMCU protocol discussed in the README 
        and documentation to set the soft-off timer of the sequence MCU.
        
        Args:
            None 

        Returns: 
            int: The soft-off timer value of the device in seconds.   
                 The soft-off timer can be configured between 1 - 1048575 seconds
                 A value < 0 indicates an error in the command or response.

        Example:
            >>> soft_off_timer = my_auto.get_soft_up_timer()
            >>> print(f"Soft Off Timer: {soft_off_timer}")
            Soft Off Timer: 5
        """
        sot_timer_cmd = self._construct_command(Kinds.GET_SOFT_OFF_TIMER)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(sot_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_SOFT_OFF_TIMER)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START: payload_end])
    
    def set_soft_off_timer(self, sot: int) -> int:
        """Set the soft-off timer value in the sequence MCU.
        
        The soft-off timer controls the number of seconds that the ignition input
        can be low before the mcu requests the system powers down via a virtual
        power button event. This method uses the LPMCU protocol discussed in the README
        and documentation to set the soft off timer of the sequence MCU.

        Args:
            sot (int): The soft off timer to set. 1 - 1048575 seconds.

        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.

        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.

        Example:
            >>> status = my_auto.set_soft_off_timer(5)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """
        self._validate_input_param(sot, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)

        set_sot_cmd = self._construct_command(Kinds.SET_SOFT_OFF_TIMER, sot.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_sot_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_SOFT_OFF_TIMER)
        if not isinstance(frame, bytes):
            return frame

        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)

    def get_hard_off_timer(self) -> int:
        """Get the existing hard-off timer value from the MCU.
        
        The number of seconds that the ignition input can be low before the MCU will
        force the system to power down. This method uses the LPMCU protocol discussed in the README
        and documentation to set the hard-off timer of the sequence MCU.

        Args:
            None

        Returns:
            int: The hard-off timer value of the device in seconds.  
                 The hard-off timer can be configured between 1 - 1048575 seconds
                 A value < 0 indicates an error in the command or response.
        Example:
            >>> hard_off_timer = my_auto.get_hard_off_timer()
            >>> print(f"Hard Off Timer: {hard_off_timer}")
            Hard Off Timer: 15
        """
        hot_timer_cmd = self._construct_command(Kinds.GET_HARD_OFF_TIMER)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(hot_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_HARD_OFF_TIMER)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)
        
        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START: payload_end])
    
    def set_hard_off_timer(self, hot: int) -> int:
        """Set the hard-off timer value in the sequence MCU.
        
        The number of seconds that the ignition input can be low before the MCU will
        force the system to power down. This method uses the LPMCU protocol discussed in the README
        and documentation to set the hard off timer of the sequence MCU.
        
        Args:
            hot (int): The hard off timer to set. 1 - 1048575 seconds.
        
        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.
        
        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.
        
        Example:
            >>> status = my_auto.set_hard_off_timer(15)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """
        self._validate_input_param(hot, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)

        set_hot_cmd = self._construct_command(Kinds.SET_HARD_OFF_TIMER, hot.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_hot_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_HARD_OFF_TIMER) 
        if not isinstance(frame, bytes):
            return frame

        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)

    def get_low_voltage_timer(self) -> int:
        """Get the existing low voltage timer value from the MCU.
        
        The low voltage timer controls the number of seconds that the measured voltage 
        can be lower than the shutdown threshold before a forced shutdown will occur. 
        This method uses the LPMCU protocol discussed in the README and documentation to set 
        the low voltage timer of the sequence MCU.
        
        Args:
            None
        
        Returns:
            int: The low voltage timer value of the device in seconds.
                    The low voltage timer can be configured between 1 - 1048575 seconds
                    A value < 0 indicates an error in the command or response.
        Example:
            >>> low_voltage_timer = my_auto.get_low_voltage_timer()
            >>> print(f"Low Voltage Timer: {low_voltage_timer}")
            Low Voltage Timer: 20
        """
        lvt_timer_cmd = self._construct_command(Kinds.GET_LOW_VOLTAGE_TIMER)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(lvt_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_LOW_VOLTAGE_TIMER)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)

        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START: payload_end]) 
    
    def set_low_voltage_timer(self, lvt: int) -> int:
        """Set the low voltage timer value in the sequence MCU.
        
        The number of seconds that the measured voltage can be lower than the shutdown
        threshold before a forced shutdown will occur. This method uses the LPMCU protocol
        discussed in the README and documentation to set the low voltage timer of the sequence MCU.
        
        Args:
            lvt (int): The low voltage timer to set. 1 - 1048575 seconds.
        
        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.
        
        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.
        
        Example:
            >>> status = my_auto.set_low_voltage_timer(20)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """
        self._validate_input_param(lvt, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)

        set_lvt_cmd = self._construct_command(Kinds.SET_LOW_VOLTAGE_TIMER, lvt.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_lvt_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_LOW_VOLTAGE_TIMER)
        if not isinstance(frame, bytes):
            return frame

        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)

    def get_shutdown_voltage(self) -> int:
        """Get the existing shutdown voltage value from the MCU.
        
        The shutdown voltage value dictates threshold voltage for triggering low-voltage
        shutdown events. This method uses the LPMCU protocol discussed in the README and documentation
        to get the shutdown voltage threshold of the sequence MCU.

        Args:
            None
        
        Returns:
            int: The shutdown voltage value of the device in centi-volts
                 The shutdown voltage can be configured between 1.000 - 48.000
                 A value < 0 indicates an error in the command or response.
        Example:
            >>> shutdown_voltage = my_auto.get_shutdown_voltage()
            >>> print(f"Shutdown Voltage: {shutdown_voltage}")
            Shutdown Voltage: 600
        """
        sdv_timer_cmd = self._construct_command(Kinds.GET_SHUTDOWN_VOLTAGE)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(sdv_timer_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_SHUTDOWN_VOLTAGE)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        _, payload_end, target_indices = self._isolate_target_indices(frame)

        ret_val = self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return self._format_response_number(frame[TargetIndices.PAYLOAD_START: payload_end]) 

    def set_shutdown_voltage(self, sdv: int) -> int:
        """Set the shutdown voltage value in the sequence MCU.
        
        The shutdown voltage value dictates threshold voltage for triggering low-voltage
        shutdown events. This method uses the LPMCU protocol discussed in the README and documentation
        to set the shutdown voltage threshold of the sequence MCU.
        
        Args:
            sdv (int): The shutdown voltage to set. 1.000 - 48.000 volts.
        
        Returns:
            int: The status of the command. 0 indicates success, < 0 indicates an error in the command or response.
        
        Raises:
            ValueError: If the input parameter is not a valid integer or is out of range.
            TypeError: If the input parameter is not of type int.
        
        Example:
            >>> status = my_auto.set_shutdown_voltage(12)
            >>> print(f"Success" if status == 0 else f"Error: {status}")
            Success
        """
        self._validate_input_param(sdv, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)

        set_sdv_cmd = self._construct_command(Kinds.SET_SHUTDOWN_VOLTAGE, sdv.to_bytes(8, 'little'), 8)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_sdv_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_SHUTDOWN_VOLTAGE) 
        if not isinstance(frame, bytes):
            return frame

        target_indices = self._isolate_target_indices(frame)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        logger.debug(f"Recieved Command Bytes: {frame}")

        return self._validate_recieved_frame(frame, target_indices, BoundaryTypes.BYTE_VALUE_RANGE)

    def get_all_automotive_settings(self, output_to_console: bool = False) -> dict:
        """Get all automotive settings from the sequence MCU.
        
        This method is a wrapper that calls all get automotive attributes and 
        formats them in one dictionary. It provides the option to print the 
        settings to the console for easy viewing, similar to the screen 
        provided in the BIOS settings. This method uses the LPMCU protocol 
        discussed in the README and documentation to get the automotive 
        settings from the sequence MCU.

        (Note numpy commenting format was used as this was the only way to get the 
        docstring to render correctly in Sphinx)
        
        Parameters
        ----------
        output_to_console : bool
            If True, print the settings to the console.

        Returns
        -------
        automotive_settings : dict
            A dictionary containing the current automotive settings of the device.
            The keys and their corresponding value types and meanings are:
            
            - ``'amd'`` (int): Current state of Automotive Mode (0 for enabled, 1 for disabled).
            - ``'lpe'`` (int): Current state of Low Power Enable (0 for enabled, 1 for disabled).
            - ``'sut'`` (int): Current setting for the Start Up Timer (Seconds).
            - ``'sot'`` (int): Current setting for the Soft Off Timer (Seconds).
            - ``'hot'`` (int): Current setting for the Hard Off Timer (Seconds).
            - ``'sdv'`` (int): Current setting for the Shutdown Voltage (millivolts).

        Examples
        --------
        >>> automotive_settings = my_auto.get_all_automotive_settings()
        >>> print(automotive_settings)
        {
            "amd": 1,
            "lpe": 1,
            "sut": 10,
            "sot": 5,
            "hot": 15,
            "sdv": 1200
        }
        """
        automotive_settings_dict = {
            "amd" : self.get_automotive_mode(),
            "lpe" : self.get_low_power_enable(),
            "sut" : self.get_start_up_timer(),
            "sot" : self.get_soft_off_timer(),
            "hot" : self.get_hard_off_timer(),
            "sdv" : self.get_shutdown_voltage(),
        }

        if output_to_console:
            for auto_label, auto_value in automotive_settings_dict.items():
                print(f"{auto_label} : {auto_value}") 
        
        return automotive_settings_dict
    
    def set_all_automotive_settings(self, setting_inputs: list) -> list:
        """Sets all automotive settings based on a provided input list of desired states.

        (Note numpy commenting format was used as this was the only way to get the 
        docstring to render correctly in Sphinx)

        Args
        ----
        setting_input : list
            A list of values corresponding to the desired states for:

            - ``automotive_mode_enabled`` (int)
            - ``low_power_enabled`` (int)
            - ``start_up_timer_seconds`` (int)
            - ``soft_off_timer_seconds`` (int)
            - ``hard_off_timer_seconds`` (int)
            - ``shutdown_voltage_mv`` (int)

        Returns
        -------
        operation_results : list
            A list of integer status codes from each ``set_*`` method, detailing 
            the outcome of each operation. The items in this list correspond to:
            
            - Result of ``set_automotive_mode()`` (int): Status code for setting automotive mode.
            - Result of ``set_low_power_enable()`` (int): Status code for enabling/disabling low power mode.
            - Result of ``set_start_up_timer()`` (int): Status code for setting the start-up timer.
            - Result of ``set_soft_off_timer()`` (int): Status code for setting the soft-off timer.
            - Result of ``set_hard_off_timer()`` (int): Status code for setting the hard-off timer.
            - Result of ``set_shutdown_voltage()`` (int): Status code for setting the shutdown voltage.

        Example
        -------
        >>> setting_inputs = [1, 1, 10, 5, 15, 12000] # 12000mV for 12.0V
        >>> results = my_auto.set_all_automotive_settings(setting_inputs)
        >>> print(results)
        [0, 0, 0, 0, 0, 0] 
        """

        if len(setting_inputs) != 6:
            raise ValueError("ERROR | setting_input must contain exactly 6 values: [amd, lpe, sut, sot, hot, sdv]")

        # Validate each input parameter
        self._validate_input_param(setting_inputs[0], BoundaryTypes.BINARY_VALUE_RANGE, int)  # amd
        self._validate_input_param(setting_inputs[1], BoundaryTypes.BINARY_VALUE_RANGE, int)  # lpe
        self._validate_input_param(setting_inputs[2], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sut
        self._validate_input_param(setting_inputs[3], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sot
        self._validate_input_param(setting_inputs[4], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # hot
        self._validate_input_param(setting_inputs[5], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sdv

        # Call individual set methods with inputs corresponding to list order
        return [
            self.set_automotive_mode(setting_inputs[0]),
            self.set_low_power_enable(setting_inputs[1]),
            self.set_start_up_timer(setting_inputs[2]),
            self.set_soft_off_timer(setting_inputs[3]),
            self.set_hard_off_timer(setting_inputs[4]),
            self.set_shutdown_voltage(setting_inputs[5]),
        ]
