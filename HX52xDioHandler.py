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
from colorama import just_fix_windows_console
from serial.tools import list_ports as system_ports
from command_set import *
from fastcrc import crc8
import datetime
import logging

class HX52xDioHandler():
    '''
    Administers the serial connection with the
    microcontroller embedded in the HX52x.
    '''
    def __init__(self, serial_connection_label:str=None):
        '''Init class by establishing serial connection.'''
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
            time.sleep(.1)
            self.__reset()
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            self.port.close()

    def __repr__(self):
        '''COM port and command set of DioInputHandler.'''
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

    def create_logger(self):
         '''Create Logger with 2 priorities'''
         if self.logger_mode == 'off':
             return
 
         self.logger = logging.getLogger()
         now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
         level_dict = { 
              'error' : logging.ERROR,
              'frames': logging.DEBUG,
               }
         
         level = level_dict.get(self.logger_mode, "Unknown")
         
         if level == 'Unknown' or level is None:
             del self.logger
             return
         
         logging.basicConfig (
             filename=f"can_session_{now}.log",
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

        self.port.write(SHELL_ACK.to_bytes(1, byteorder='little'))
        while current_time - initial_time <= TIME_THRESHOLD and nack_count < NACKS_NEEDED:
            current_time = time.time()
            if self.port.inWaiting() > 0:
                # If received byte is not what was expected, reset counter
                byte_in_port = self.port.read(1)
                if int.from_bytes(byte_in_port, byteorder='little') == SHELL_NACK:
                    # print(bytes_in_port) # Should be NACKS...
                    nack_count += 1
                    self.port.write(SHELL_ACK.to_bytes(1, byteorder='little'))
                    time.sleep(.004)

        if nack_count == NACKS_NEEDED:
            print("\033[32mDIO Interface Found\033[0m")
            return

        print(f"\033[91mERROR | AKNOWLEDGEMENT ERROR: "\
              f"mismatch in number of nacks, check if {self.serial_connection_label} "\
              f"is the right port?\033[0m")

        raise ValueError("ERROR | AKNOWLEDGEMENT ERROR")

    def __reset(self, nack_counter:int=NUM_NACKS, reset_buffers:bool=True) -> None:
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
            self.port.write(SHELL_ACK.to_bytes(1, byteorder='little'))
            bytes_sent += 1
            byte_in_port = self.port.read(1)

            # If received byte is not what was expected, reset counter
            if int.from_bytes(byte_in_port, byteorder='little') == SHELL_NACK:
                bytes_to_send -= 1
            else:
                bytes_to_send = nack_counter

    def validate_message_params(self, kind:Kinds, *payload:int):
        pass

    def validate_recieved_frame(self, input_command:bytes, kind:Kinds):
        pass

    # @lru_cache(maxsize=128)
    def __construct_command(self, kind:Kinds, *payload:int) -> bytes:
        
        self.validate_message_params(kind, payload)
        
        crc_calculation = crc8.smbus((bytes([len(payload), kind, *payload])))
        
        constructed_command = bytes([ShellParams.SHELL_SOF, 
                                     crc_calculation, 
                                     len(payload), 
                                     kind, 
                                     *payload
                                     ])    
        
        print("Construct Command", constructed_command)
        return constructed_command

    def __send_command(self, command_to_send:bytes) -> bool:
        # send command byte by byte and validate response
        shell_ack_cnt = 0
        for byte in command_to_send:
            self.port.write(byte.to_bytes(1, byteorder='little'))
            byte_in_port = self.port.read(1)
            
            if int.from_bytes(byte_in_port, byteorder='little') == SHELL_ACK:
                shell_ack_cnt += 1

        if shell_ack_cnt == len(command_to_send):
            return True

        print("\033[91mERROR | AKNOWLEDGEMENT ERROR: "\
              "mismatch in number of aknowledgements, reduce access speed?\033[0m")
        
        return False

    def __receive_command(self, response_frame_len=RESPONSE_FRAME_LEN) -> bytes:
        '''\
        receive command in expected format that complies with UART Shell.
        The response_frame list should always end with a NACK ['\a'] 
        command indicating the end of the received payload.
        '''
        response_frame = []
        self.port.write(SHELL_ACK.to_bytes(1, byteorder='little')) 
        for _ in range(response_frame_len): 
            byte_in_port = self.port.read(1)
            response_frame.append(byte_in_port)
            self.port.write(SHELL_ACK.to_bytes(1, byteorder='little')) 
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
        if di_pin < 0 or di_pin > 7:
            raise ValueError(f"\033[91mOut of Range Pin Value Provided: {di_pin}. Valid Range [0-7]\033[0m")

        di_command = self.__construct_command(Kinds.GET_DI, di_pin)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(di_command):
            return -1

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False) # why reset twice
        time.sleep(.004)

        # Retrieve di value located in penultimate idx of frame
        val = frame[-2]
        if val in [0, 1]:
            return val

        print("\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    
    def get_do(self, do_pin:int) -> int:
        if do_pin < 0 or do_pin > 7:
            raise ValueError(f"\033[91mOut of Range Pin Value Provided: {do_pin}. Valid Range [0-3]\033[0m")

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
        val = frame[-2]
        if val in [0, 1]:
            return val

        print("\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -2

    def set_do(self, pin:int, value:int) -> int:
        if pin < 0 or pin > 7:
            raise ValueError(f"\033[91mOut of Range Pin Value Provided: {pin}. Valid Range [0-7]\033[0m")
        if value not in [0, 1]:
            raise ValueError(f"\033[91mOut of Range Value Provided: {value}. Valid Range [0-1]\033[0m")
        
        set_do_command = self.__construct_command(Kinds.GET_DO, pin, value)
        
        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)

        if not self.__send_command(set_do_command):
            return -1

        frame = self.__receive_command()

        self.__reset(nack_counter=64, reset_buffers=False)
        
        print(f"Recieved Command {frame}")

        # TODO: valid check here
        # print(bytes(frame[:-1]))
        # if bytes(frame[:-1]) != set_do_command:
        #     print(f"\033[91mERROR | SEND CONFIRMATION FAILURE\033[0m")
        #     return -3

        return 0

    def get_di_contact(self) -> int: # An error occurred: 'set' object is not callable, why       
        di_contact_state_cmd = self.__construct_command(Kinds.GET_DI_CONTACT)
        
        self.__reset(nack_counter=64)
        if not self.__send_command(di_contact_state_cmd):
            return -1
        
        frame = self.__receive_command()
        print(frame)

        self.__reset(nack_counter=64, reset_buffers=False) 
        time.sleep(.004)

        # Retrieve di value located in penultimate idx of frame
        val = frame[-2]
        if val in [0, 1]:
            return val
        
        print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    def get_do_contact(self) -> int:

        do_contact_state_cmd = self.__construct_command(Kinds.GET_DO_CONTACT)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(do_contact_state_cmd):
            return -1
        
        frame = self.__receive_command()
        
        self.__reset(nack_counter=64, reset_buffers=False) # why reset twice in get_di command
        time.sleep(.004)

        print(i for i in frame)
        
        # Retrieve di value located in penultimate idx of frame
        val = frame[-2]
        if val in [0, 1]:
            return val
        
        print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1

    def set_di_contact(self, contact_type:int) -> int:
            if contact_type < 0 or contact_type > 1:
                raise ValueError(f"\033[91mOut of Range Contact Type Provided: {contact_type}. Valid Range [0-1]\033[0m")
            
            set_di_contact_state_cmd = self.__construct_command(Kinds.SET_DI_CONTACT, contact_type)

            # Enclose each value read with buffer clearances
            self.__reset(nack_counter=64)

            if not self.__send_command(set_di_contact_state_cmd):
                return -1
            
            frame = self.__receive_command()
            
            self.__reset(nack_counter=64, reset_buffers=False)
            time.sleep(.004)
            
            # validate

            print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
            return -1

    def set_do_contact(self, contact_type:int) -> int:
        if contact_type < 0 or contact_type > 1:
            raise ValueError(f"\033[91mOut of Range Contact Type Provided: {contact_type}. Valid Range [0-1]\033[0m")
        
        set_di_contact_state_cmd = self.__construct_command(Kinds.GET_DI_CONTACT, contact_type)

        # Enclose each value read with buffer clearances
        self.__reset(nack_counter=64)
        if not self.__send_command(set_do_contact_commands, contact_type):
            return -1
        
        frame = self.__receive_command()
        
        self.__reset(nack_counter=64, reset_buffers=False)
        time.sleep(.004)

        print(frame)
        
        # TODO: Generate check
        
        print(f"\033[91mERROR | NON-BINARY DATATYPE DETECTED\033[0m")
        return -1
    
    def show_all_io_states(self):
        pass

    def set_all_outputs(self, do_lst:list) -> int:
        pass

    def get_all_inputs(self) -> list:
        pass