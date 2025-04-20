from command_set import ProtocolConstants, Kinds, StatusTypes
from OnLogicNuvotonManager import OnLogicNuvotonManager
import time 
import logging

class AutomotiveHandler(OnLogicNuvotonManager):
    def __init__(self, logger_mode:str=None, handler_mode:str=None, serial_connection_label=None):
        super().__init__(logger_mode=logger_mode, 
                        handler_mode=handler_mode, 
                        serial_connection_label=serial_connection_label
                        )


    '''
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
    '''
