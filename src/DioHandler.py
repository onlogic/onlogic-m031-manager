from OnLogicNuvotonManager import OnLogicNuvotonManager

import time
import serial

from abc import abstractmethod
from LoggingUtil import logging
from serial.tools import list_ports as system_ports
from command_set import ProtocolConstants, Kinds, StatusTypes
from colorama import Fore

class DioHandler(OnLogicNuvotonManager):
    def __init__(self, logger_mode:str=None, handler_mode:str=None, serial_connection_label=None):
        super().__init__(logger_mode=logger_mode, 
                         handler_mode=handler_mode, 
                         serial_connection_label=serial_connection_label
                         )

    def _init_port(self) -> None:
        super()._init_port()

    def _mcu_connection_check(self) -> None:
        super()._mcu_connection_check()
        
        #if self.get_di(0) not in [0,1]:
        #    raise ValueError("Error | Incorrect Value returned, is this the right device?")

    def get_di(self, di_pin:int) -> int:
        """\
        User-facing method to get state of digital inputs.

        :param self:    instance of the class
        :param di_pin:  digital input pin with range [0-7]
        :return:        returns 1, indicating on, 0, indicating off, 
                        and -1, indicating an error occured in the sample
        """
        self._validate_input_param(di_pin, [0,7], int)

        di_command = self._construct_command(Kinds.GET_DI, di_pin)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(di_command):
            return StatusTypes.SUCCESS

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

        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return StatusTypes.SUCCESS

    def get_di_contact(self) -> int:
        di_contact_state_cmd = self._construct_command(Kinds.GET_DI_CONTACT)

        self._reset(nack_counter=64)
        if not self._send_command(di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[-2]

    def get_do_contact(self) -> int:
        do_contact_state_cmd = self._construct_command(Kinds.GET_DO_CONTACT)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(do_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return frame[-2]

    def set_di_contact(self, contact_type:int) -> int:
        self._validate_input_param(contact_type, [0,1], int)

        set_di_contact_state_cmd = self._construct_command(Kinds.SET_DI_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)

        if not self._send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)

        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
        if ret_val is not StatusTypes.SUCCESS:
            return ret_val

        return StatusTypes.SUCCESS

    def set_do_contact(self, contact_type:int) -> int:
        self._validate_input_param(contact_type, [0,1], int)

        set_di_contact_state_cmd = self._construct_command(Kinds.SET_DO_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self._reset(nack_counter=64)
        if not self._send_command(set_di_contact_state_cmd):
            return StatusTypes.SEND_CMD_FAILURE

        frame = self._receive_command(6)
 
        self._reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        self.logger_util._log_print(f"recieved command bytestr {frame}",
                        print_to_console=False,
                        log=True,
                        level=logging.DEBUG
                        )

        ret_val = self._validate_recieved_frame(frame, -2, [0,1])
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

        status_codes = []
        for do_lst_idx, do_lst_val in enumerate(do_lst):
            status_codes.append(self.set_do(do_lst_idx, do_lst_val))

        return status_codes
