import sys
import logging
from datetime import datetime
from typing import Optional
from colorama import Fore, init

class LoggingUtil():
    def __init__(self, logger_mode, handler_mode):
        self.logger_mode = logger_mode
        self.handler_mode = handler_mode
        self.logger = None
        
    def _create_logger(self):# -> logging.RootLogger:
        '''Create Logger with INFO, DEBUG, and ERROR Debugging'''
        if self.logger_mode in [None, "off"]:
            print("Logger Mode off, ignoring")
            return

        if self.logger_mode not in ['info', 'debug','error']:
            print("Logger Mode", self.logger_mode)
            raise ValueError("ERROR | Invalid logger_mode")
        
        now = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        filename=f"HX52x_session_{now}.log"

        handlers = []
        if self.handler_mode == "both":
            handlers.extend([logging.FileHandler(filename), 
                            logging.StreamHandler(sys.stdout)])
        elif self.handler_mode == "console":
            handlers.append(logging.StreamHandler(sys.stdout))
        elif self.handler_mode == "file":
            handlers.append(logging.FileHandler(filename))
        else:
            raise ValueError("ERROR | Incorrect Handle Parameter Provided") 
        
        self.logger = logging.getLogger()
    
        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }
        
        level = level_dict.get(self.logger_mode, "Unknown")

        if level == 'Unknown' or level is None:
            self.logger_mode = 'off'
            del self.logger
            raise ValueError("ERROR | Invalid logger_mode")
        
        logging.basicConfig (
            format='[%(asctime)s %(levelname)s %(filename)s %(message)s',
            level=level,
            handlers=handlers  
        )

        self._log_print(f"Logger Initialized...",
                         print_to_console=False,
                         log=True,
                         level=logging.INFO
                        )

    @staticmethod
    def _format_log_message(message_info):
        frame = sys._getframe(3)
        lineno = frame.f_lineno
        function = frame.f_code.co_name
        return f":{lineno} -> {function}()] {message_info}"

    def _log_print(self, message_info:str, print_to_console:bool=True, color:str=None, 
                    log:bool=False, level:Optional[int]=None) -> bool:
        if print_to_console and self.logger_mode != "console":
            if color == Fore.RED:
                print(Fore.RED + message_info)
            elif color == Fore.GREEN:
                print(Fore.GREEN + message_info)
            else:
                print(message_info)

        if log is True \
                and level is not None \
                and self.logger_mode not in ["off", None]:

            log_msg = self._format_log_message(message_info)

            if level == logging.INFO:
                self.logger.info(log_msg)
            elif level == logging.DEBUG:
                self.logger.debug(log_msg)
            elif level == logging.ERROR:
                self.logger.error(log_msg)
            else:
                raise ValueError("ERROR | INCORRECT MODE INPUT INTO LOGGER")