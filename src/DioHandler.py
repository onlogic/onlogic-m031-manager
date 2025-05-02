import time
import serial
from OnLogicNuvotonManager import OnLogicNuvotonManager
from LoggingUtil import logging
from command_set import TargetIndices, ProtocolConstants, Kinds, StatusTypes, BoundaryTypes
from colorama import Fore

class DioHandler(OnLogicNuvotonManager):
    def __init__(self, logger_mode: str = None, handler_mode: str = None, serial_connection_label: str = None):
        super().__init__(logger_mode=logger_mode, 
                         handler_mode=handler_mode, 
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
                self.logger_util._log_print(type_connect_error, print_to_console=True,
                                            color=Fore.RED, log=True, level=logging.ERROR)
                raise TypeError(type_connect_error)

        except serial.SerialException as e:
            serial_connect_err = f"ERROR | {e}: Are you on the right port?"
            self.logger_util._log_print(serial_connect_err, print_to_console=True,
                                        color=Fore.RED, log=True, level=logging.ERROR)
            raise serial.SerialException(serial_connect_err)

    def get_info(self) -> None:
        super()._read_files(filename="DioHandlerDescription.log")

    def _mcu_connection_check(self) -> None:
        super()._mcu_connection_check()
        
        #if self.get_di(0) not in BoundaryTypes.BINARY_VALUE_RANGE:
        #    raise ValueError("Error | Incorrect Value returned, is this the right device?")

    def get_di(self, di_pin: int) -> int:
        """\
        User-facing method to get state of digital inputs.

        :param self:    instance of the class
        :param di_pin:  digital input pin with range [0-7]
        :return:        returns 0, indicating on, 1, indicating off, 
                        and StatusTypes.SEND_CMD_FAILURE if command send failed.
        :rtype:         int
        :raises ValueError: if di_pin is not in the range of 0-7
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

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        # Retrieve do value located in penultimate idx of frame
        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def get_do(self, do_pin: int) -> int:
        self._validate_input_param(do_pin, BoundaryTypes.DIGITAL_IO_PIN_RANGE, int)

        do_command = self._construct_command(Kinds.GET_DO, do_pin)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DO)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        # Retrieve do value located in penultimate idx of frame
        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_do(self, pin: int, value: int) -> int:
        self._validate_input_param(pin, BoundaryTypes.DIGITAL_IO_PIN_RANGE, int)
        self._validate_input_param(value, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_do_command = self._construct_command(Kinds.SET_DO, pin, value)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)

        if not self._send_command(set_do_command):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_DO)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def get_di_contact(self) -> int:
        di_contact_state_cmd = self._construct_command(Kinds.GET_DI_CONTACT)

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DI_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False) 
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def get_do_contact(self) -> int:
        do_contact_state_cmd = self._construct_command(Kinds.GET_DO_CONTACT)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
        if not self._send_command(do_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.GET_DO_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[TargetIndices.PENULTIMATE]

    def set_di_contact(self, contact_type: int) -> int:
        self._validate_input_param(contact_type, BoundaryTypes.BINARY_VALUE_RANGE, int)

        set_di_contact_state_cmd = self._construct_command(Kinds.SET_DI_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES)
    
        if not self._send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(Kinds.SET_DI_CONTACT)
        if not isinstance(frame, bytes):
            return frame

        self._reset(nack_counter=ProtocolConstants.STANDARD_NACK_CLEARANCES, reset_buffers=False)
        time.sleep(ProtocolConstants.STANDARD_DELAY)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def set_do_contact(self, contact_type: int) -> int:
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

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        return self._validate_recieved_frame(frame, TargetIndices.PENULTIMATE, BoundaryTypes.BINARY_VALUE_RANGE)

    def get_all_input_states(self) -> list:
        '''
        all_input_states = []
        
        for i in range(0, 8):
            all_input_states.append()

        return all_input_states
        '''

        return [self.get_di(state) for state in range(0, 8)]


    def get_all_output_states(self) -> list:
        '''
        all_output_states = []

        for i in range(0, 8):
            all_output_states.append(self.get_do(i))

        return all_output_states
        '''
        return [self.get_do(state) for state in range(0, 8)]


    def get_all_io_states(self) -> list:
        return [self.get_all_input_states(), self.get_all_output_states()]

    def set_all_output_states(self, do_lst:list) -> list:
        '''
        if len(do_lst) < 8:
            raise ValueError("ERROR | Incorrect amount of inputs specified.")

        status_codes = []
        for do_lst_idx, do_lst_val in enumerate(do_lst):
            status_codes.append(self.set_do(do_lst_idx, do_lst_val))
        '''
        return [self.set_do(do_lst_idx, do_lst_val) for do_lst_idx, do_lst_val in enumerate(do_lst)]
