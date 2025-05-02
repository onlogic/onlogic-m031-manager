import time
import serial
import logging
from OnLogicNuvotonManager import OnLogicNuvotonManager
from command_set import ProtocolConstants, Kinds, StatusTypes, TargetIndices, BoundaryTypes

logger = logging.getLogger(__name__)

class AutomotiveHandler(OnLogicNuvotonManager):
    def __init__(self, serial_connection_label = None):
        super().__init__(
                         serial_connection_label=serial_connection_label
                        )

    def get_info(self) -> None:
        super()._read_files(filename="AutomotiveModeDescription.log")

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

    def _init_port_error_handling(self, error_msg: str, return_early: bool = False) -> None | ValueError:
        logger.error(error_msg, level=logging.ERROR)
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
            return serial.Serial(self.serial_connection_label, ProtocolConstants.BAUDRATE, timeout=1)
        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?" \
                                  "Did you enable correct bios settings []?"
            self._init_port_error_handling(serial_connect_err, return_early=True)
            raise serial.SerialException(serial_connect_err)
        
    def get_info(self) -> None:
        super().get_info(filename="AutomotiveModeDescription.log")

    def get_automotive_mode(self) -> int:
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
    
    def set_automotive_mode(self, amd: int):
        self._validate_input_param(amd, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_auto_mode = self._construct_command(Kinds.SET_AUTOMOTIVE_MODE, amd)

        # Enclose each value read with buffer clearances
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

    def get_low_power_enable(self):
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

    def get_soft_off_timer(self):
        sot_timer_cmd = self._construct_command(Kinds.GET_SOFT_OFF_TIMER)

        # Enclose each value read with buffer clearances
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

    def get_hard_off_timer(self):
        hot_timer_cmd = self._construct_command(Kinds.GET_HARD_OFF_TIMER)

        # Enclose each value read with buffer clearances
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

    def get_low_voltage_timer(self):
        lvt_timer_cmd = self._construct_command(Kinds.GET_LOW_VOLTAGE_TIMER)

        # Enclose each value read with buffer clearances
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
        self._validate_input_param(lvt, BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)

        set_lvt_cmd = self._construct_command(Kinds.SET_LOW_VOLTAGE_TIMER , lvt.to_bytes(8, 'little'), 8)

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

    def get_shutdown_voltage(self):
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
        automotive_settings_dict = {
            "amd" : self.get_automotive_mode(),
            "lpe" : self.get_low_power_enable(),
            "sut" : self.get_start_up_timer(),
            "sot" : self.get_soft_off_timer(),
            "hot" : self.get_hard_off_timer(),
            "sdv" : self.get_shutdown_voltage(),
        }

        if output_to_console:
            for am_label, am_value in automotive_settings_dict.items():
                print(f"{am_label} : {am_value}") 
        
        return automotive_settings_dict
    
    def set_all_automotive_settings(self, setting_input: list) -> list:
        """
        Sets all automotive settings based on the provided input list.

        Args:
            setting_input (list): A list of values corresponding to:
                [amd, lpe, sut, sot, hot, sdv].

        Returns:
            list: A list of results from each `set_*` method, particularly:

            + set_automotive_mode
            + set_low_power_enable
            + set_start_up_timer
            + set_soft_off_timer
            + setting_input
            + set_shutdown_voltage

        """

        if len(setting_input) != 6:
            raise ValueError("ERROR | setting_input must contain exactly 6 values: [amd, lpe, sut, sot, hot, sdv]")

        # Validate each input parameter
        self._validate_input_param(setting_input[0], BoundaryTypes.BINARY_VALUE_RANGE, int)  # amd
        self._validate_input_param(setting_input[1], BoundaryTypes.BINARY_VALUE_RANGE, int)  # lpe
        self._validate_input_param(setting_input[2], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sut
        self._validate_input_param(setting_input[3], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sot
        self._validate_input_param(setting_input[4], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # hot
        self._validate_input_param(setting_input[5], BoundaryTypes.AUTOMOTIVE_TIMER_RANGE, int)  # sdv

        # Call individual set methods with inputs corresponding to list order
        return [
            self.set_automotive_mode(setting_input[0]),
            self.set_low_power_enable(setting_input[1]),
            self.set_start_up_timer(setting_input[2]),
            self.set_soft_off_timer(setting_input[3]),
            self.set_hard_off_timer(setting_input[4]),
            self.set_shutdown_voltage(setting_input[5]),
        ]
