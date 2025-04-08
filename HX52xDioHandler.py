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
        + public method:  get_di_contact
        + public method:  set_di_contact  

References:
    https://fastcrc.readthedocs.io/en/latest/
'''

import time
import serial
import functools
import datetime
import logging

from colorama import just_fix_windows_console
from serial.tools import list_ports as system_ports
from command_set import ProtocolConstants, Kinds, StatusTypes, MCU_VID_PID, TIME_THRESHOLD
from fastcrc import crc8

class HX52xDioHandler():
    '''
    Administers the serial connection with the
    microcontroller embedded in the K/HX-52x DIO-Add in Card.
    '''
    def __init__(self, serial_connection_label:str=None, logger_mode:str="off"):
        '''Init class by establishing serial connection.'''
        self.logger_mode = logger_mode   
        self.__create_logger()
        just_fix_windows_console() # Color coding for errors and such
        self.is_setup=False
        self.serial_connection_label = serial_connection_label
        self.port = self.__init_port()
        self.__mcu_connection_check()
        self.is_setup=True
        self.__reset()

    def __del__(self):
        '''Destroy the object and end device communication gracefully.'''
        if self.is_setup:
            self.close_dio_connection()

    def __repr__(self):
        '''COM port and command set of DioInputHandler.'''
        # TODO: Flesh this out
        # serial.__version__
        return f"\nPort: {self.serial_connection_label}\n"
    
    def __get_device_port(self, dev_id:str, location:str=None) -> str:
        """Scan and return the port of the target device."""
        all_ports = system_ports.comports() 
        for port in sorted(all_ports):
            if dev_id in port.hwid:
                if location and location in port.location:
                    print(f"Port: {port}\n"
                          f"Port Location: {port.location}\n"
                          f"Hardware ID: {port.hwid}\n"
                          f"Device: {port.device}\n"
                          )
                    return port.device
        return None
    
    def __init_port(self) -> serial.Serial:
        '''Init port and establish USB-UART connection.'''
        if self.serial_connection_label is None:
            self.serial_connection_label = self.__get_device_port(MCU_VID_PID, ".0")

        try:
            return serial.Serial(self.serial_connection_label, 115200, timeout=1)
        except serial.SerialException as e:
            raise serial.SerialException(f"\033[91mERROR | {e}: Are you on the right port?\033[0m")

    def __create_logger(self):
        '''Create Logger with INFO, DEBUG, and ERROR Debugging'''
        if self.logger_mode == 'off':
            return
          
        self.logger = logging.getLogger()
        now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }

        level = level_dict.get(self.logger_mode, "Unknown")

        if level == 'Unknown' or level is None:
            del self.logger
            return

        logging.basicConfig (
            filename=f"HX52x_session_{now}.log",
            format='[%(asctime)s %(levelname)s %(filename)s:%(lineno)d -> %(funcName)s()] %(message)s',
            level=level
        )

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
        while current_time - initial_time <= TIME_THRESHOLD and nack_count < ProtocolConstants.NACKS_NEEDED:
            current_time = time.time()
            if self.port.inWaiting() > 0:
                # If received byte is not what was expected, reset counter
                byte_in_port = self.port.read(1)
                if int.from_bytes(byte_in_port, byteorder='little') == ProtocolConstants.SHELL_NACK:
                    # print(bytes_in_port) # Should be NACKS...
                    nack_count += 1
                    self.port.write(ProtocolConstants.SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(.004)

        if nack_count == ProtocolConstants.NACKS_NEEDED:
            print("\033[32mDIO Interface Found\033[0m")
            return

        print(f"\033[91mERROR | AKNOWLEDGEMENT ERROR: "\
              f"mismatch in number of nacks, check if {self.serial_connection_label} "\
              f"is the right port?\033[0m")

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
                raise RuntimeError("Cannot recover MCU")
            
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
            raise TypeError(f"\033[91mERROR | {type(dio_input_parameter)} was found when {input_type} was expected\033[0m")
            
        if dio_input_parameter < valid_input_range[0] or dio_input_parameter > valid_input_range[1]:
            raise ValueError(f"\033[91mERROR | Out of Range Value Provided: {dio_input_parameter}. Valid Range {valid_input_range}\033[0m")
    
    def __log_print(self, message_info, print_to_console=True, log=False, level=False):
        if print_to_console:
            print(message_info)

        if log is not None and level is not None:
            if level == logging.INFO:
                self.logger.info(message_info)
            elif level == logging.DEBUG:
                self.logger.debug(message_info)
            elif level == logging.ERROR:
                self.logger.error(message_info)
            else:
                raise ValueError("INCORRECT MODE INPUT INTO LOGGER")

    def __check_crc(self, frame:bytes) -> bool:
        if len(frame) < 4:
            return False
        
        crc_bytes = frame[2:-1]
        crc_val = crc8.smbus(crc_bytes)

        print(crc_val)

        if crc_val != frame[1]:
            return False

        return True

    def __validate_recieved_frame(self, return_frame:list, target_index:int=None, target_range:list=None) -> int:
        if return_frame[-1] != ProtocolConstants.SHELL_NACK:
            return StatusTypes.RECV_FRAME_NACK_ERROR

        is_crc = self.__check_crc(return_frame)
        if is_crc:
            return StatusTypes.RECV_FRAME_CRC_ERROR
        
        if target_index is not None:
            if return_frame[target_index] not in target_range:
                return StatusTypes.RECV_NONBINARY_DATATYPE_DETECTED

        return StatusTypes.SUCCESS

    def close_dio_connection(self):
        # HX52xDioHandler.__construct_command.cache_clear()
        # TODO: Figure out why is the sleep function Erroring when lru_cache is enabled in destructor
        # time.sleep(.001) 
        self.__reset()
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()
        self.port.close()

    @functools.lru_cache(maxsize=128)
    def __construct_command(self, kind:Kinds, *payload:int) -> bytes:
        # self.__validate_message_bytes(kind, payload)
        
        crc_calculation = crc8.smbus((bytes([len(payload), kind, *payload])))
        
        constructed_command = bytes([ProtocolConstants.SHELL_SOF, 
                                     crc_calculation, 
                                     len(payload), 
                                     kind, 
                                     *payload
                                     ])
        
        print("Constructed Command", constructed_command)
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
            return True # StatusTypes.SUCCESS

        print("\033[91mERROR | AKNOWLEDGEMENT ERROR: "\
              "mismatch in number of aknowledgements, reduce access speed?\033[0m")
        
        return False # StatusTypes.SEND_CMD_FAILURE

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
        print(response_frame)
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
            return -1

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        # Retrieve di value located in penultimate idx of frame
        val = frame[-2]
        if val in [0, 1]:
            return val

        print("\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    
    def get_do(self, do_pin:int) -> int:
        self.__validate_input_param(do_pin, [0,7], int)

        do_command = self.__construct_command(Kinds.GET_DO, do_pin)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(do_command):
            return -1

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        print(frame)
        # Retrieve di value located in penultimate idx of frame
        # ret_val = self.__validate_recieved_frame(frame, -2, [0,1])
        # if ret_val is not StatusTypes.RECV_SUCCESS:
        #     return ret_val
        
        return frame[-2]

    def set_do(self, pin:int, value:int) -> int:
        self.__validate_input_param(pin, [0,7], int)
        self.__validate_input_param(value, [0,1], int)
        
        set_do_command = self.__construct_command(Kinds.GET_DO, pin, value)
        
        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)

        if not self.__send_command(set_do_command):
            return -1

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        
        print(f"Recieved Command {frame}")

        #TODO Move into validation function
        # if frame[-2] not in [0, 1] or frame[-1] != ProtocolConstants.SHELL_NACK:
        #     print(f"\033[91mERROR | SEND CONFIRMATION FAILURE\033[0m")
        #     return -3

        return 0

    def get_di_contact(self) -> int:
        di_contact_state_cmd = self.__construct_command(Kinds.GET_DI_CONTACT)
        
        self.__reset(nack_counter=64)
        if not self.__send_command(di_contact_state_cmd):
            return -1
        
        frame = self.__receive_command(6)
        print(frame)

        self.__reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        # Retrieve di value located in penultimate idx of frame
        # val = frame[-2]
        # if val in [0, 1]:
        #     return val
        
        print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    def get_do_contact(self) -> int:
        do_contact_state_cmd = self.__construct_command(Kinds.GET_DO_CONTACT)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(do_contact_state_cmd):
            return -1
        
        frame = self.__receive_command(6)
        
        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        print(frame)
        print(self.__check_crc(frame))

        # Retrieve di value located in penultimate idx of frame
        # val = frame[-2]
        # if val in [0, 1]:
        #     return val
        
        print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    def set_di_contact(self, contact_type:int) -> int:
        self.__validate_input_param(contact_type, [0,1], int)
        
        set_di_contact_state_cmd = self.__construct_command(Kinds.SET_DI_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)

        if not self.__send_command(set_di_contact_state_cmd):
            return -1

        frame = self.__receive_command(6)

        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        # validate HERE

        return 0

    def set_do_contact(self, contact_type:int) -> int:
        self.__validate_input_param(contact_type, [0,1], int)

        set_di_contact_state_cmd = self.__construct_command(Kinds.SET_DO_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(set_di_contact_state_cmd):
            return -1

        frame = self.__receive_command(6)
                
        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        # Validate HERE

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

    def set_all_output_states(self, do_lst:list) -> int:
        for i in do_lst:
            self.set_do(i)

        return StatusTypes.SUCCESS