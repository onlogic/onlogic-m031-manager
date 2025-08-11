# -*- coding: utf-8 -*-
"""An optional logging utility for the OnLogic M031 Manager.

This module provides the optional LoggingUtil class, which is designed to 
configure and manage logging for the OnLogic M031 Manager. 

Note:
    it is completely optional and not required for the use of the OnLogic M031 Manager,
    but is provided for convenience and ease of use. The user can make create their own custom
    logger if desired.
"""

import sys
import logging
from datetime import datetime
from typing import Optional
import os

class LoggingUtil():
    """LoggingUtil class for configuring logging in the OnLogic M031 Manager.

    This class provides methods to set up a logger with a specified name, level, and handlers.

    Attributes:
        logger_name (str): The name of the logger. It is converted to lowercase and stripped of whitespace.
                           Note, please use 'root' for the root logger unless you are willing to add a field 
                           to the target class to allow for a custom logger utility. 
        logger_level (str): The logging level (e.g., 'info', 'debug', 'error').
                            It is converted to lowercase and stripped of whitespace.          
        handler_mode (str): The mode for the handler (e.g., 'console', 'file', 'both').
                            It is converted to lowercase and stripped of whitespace.
        logger (logging.Logger): The configured logger instance.

        format (str): The format for log messages, specified in the initialization of the class.

    Example:
        For debug logging to console:

            config_logger = LoggingUtil(
                logger_name='root',
                logger_level="DEBUG", 
                handler_mode="CONSOLE",
            )

            config_logger.config_logger_elements()

        For info logging to file:

            config_logger = LoggingUtil(
                logger_name='root',
                logger_level="INFO", 
                handler_mode="FILE",
                log_directory="logs"
            )

            config_logger.config_logger_elements()

        For error logging to both console and file:

            config_logger = LoggingUtil(
                logger_name='root',
                logger_level="ERROR", 
                handler_mode="BOTH",
                log_directory="logs"
            )

            config_logger.config_logger_elements()
    """
    def __init__(self, logger_name: str, logger_level: str, handler_mode: str, log_directory: str = None):
        """Initialize the LoggingUtil class with the specified logger name, level, and handler mode.
        Args:
            logger_name (str): The name of the logger. It is converted to lowercase and stripped of whitespace.
                               Note, please use 'root' for the root logger unless you are willing to add a field 
                               to the target class to allow for a custom logger utility. 
            logger_level (str): The logging level (e.g., 'info', 'debug', 'error').
                                It is converted to lowercase and stripped of whitespace.          
            handler_mode (str): The mode for the handler (e.g., 'console', 'file', 'both').
                                It is converted to lowercase and stripped of whitespace.
            log_directory (str): The directory where log files will be stored. 
                                 If None, no file handler will be created.
                                 It is cleaned of invalid characters and stripped of whitespace.
                                 Defaults to None.
        """
        self.logger_name  = logger_name
        self.logger_level  = self.__handle_lconfig_str(logger_level)
        self.handler_mode = self.__handle_lconfig_str(handler_mode)
        self.log_directory = self.__handle_ldirectory_str(log_directory)
        self.logger = None
        self.format = '[%(asctime)s %(levelname)s %(filename)s:%(lineno)d -> %(funcName)s()] %(message)s'
        
    @staticmethod
    def __handle_lconfig_str(input_str: str) -> str | None:
        '''
        Clean string input for logger_name, logger_level, and handler_mode. 
        Note: method is private and name mangled
        '''
        return input_str.lower().strip() if isinstance(input_str, str) else input_str

    def __handle_ldirectory_str(self, input_str: str | None) -> str | None:
        '''
        Clean string input for log_directory. 
        Note: method is private and name mangled
        '''
        if input_str is None or self.handler_mode in [None, "off", "console"]:
            return None
        
        if not isinstance(input_str, str):
            return None

        input_str = input_str.strip()

        # Remove invalid characters for directory names, linux can handle most these, but windows cannot
        invalid_chars = r'<>:"/\\|?*'

        for char in invalid_chars:
            input_str = input_str.replace(char, '')

        # Ensure the directory path is not empty after cleaning
        if not input_str:
            raise ValueError("ERROR | log_directory cannot be empty after cleaning invalid characters.")

        return input_str
        
    def _create_filename(self, log_directory: str = None) -> str:
        '''Create a filename for the log file. Note: method is private and name mangled.'''
        base_log_file_name = f"log_session_{datetime.now().strftime("%m_%d_%Y_%H_%M_%S")}.log"

        if log_directory:
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            base_log_file_name = os.path.join(log_directory, base_log_file_name)

        return base_log_file_name

    def _get_logger_level(self) -> int | None:
        """Get the logger level based on the provided logger_level string

        Args:
            logger_level (str): The desired logging level as a string.
                Options: 'info', 'debug', 'error', or None to disable logging.

        Returns:
            int: The corresponding logging level constant data type from the logging module.
                Returns None if logger_level is 'off' or None if a logger value 
                is not found.

        Raises:
            ValueError: If an invalid logger_level is provided.
        """
        if self.logger_level in [None, "off"]:
            print("Logger Mode off, ignoring")
            return None

        if self.logger_level not in ['info', 'debug','error']:
            print("Logger Mode", self.logger_level)
            raise ValueError("ERROR | Invalid logger_level")

        level_dict = { 
            'info'  : logging.INFO,
            'debug' : logging.DEBUG,
            'error' : logging.ERROR,
            }

        level = level_dict.get(self.logger_level, None)

        return level

    def _config_handlers(self, filename: str) -> list:
        """Configure the logging handlers based on the provided handler_mode
        
        Args:
            filename (str): The name of the log file to be used if file handler is selected.
        
        Returns:
            list: A list of configured logging handlers.
        """
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

        return handlers

    def config_logger_elements(self) -> Optional[logging.Logger]:
        """Configure the logger with the specified name, level, and handlers.

        This method will set up a logger based on logging configurations
        provided to the LoggingUtil class constructor. It supports 3 logging 
        level configurations, DEBUG, INFO, and ERROR. And the log messages can be
        directed at the Console, an external file, or both.

        It chooses the file handler object based off cleaned input mode selection.
        The format of the logger is set to match the default format defined in the class.
        After, it will set the logger as a null handler if there is handler objects configured.
        It will make sure not to propogate the logging configurations or messages to other loggers.

        Params:
            None

        Returns:
            logging.Logger: The configured logger instance.

        Example:
            config_logger = LoggingUtil(
                logger_name='root',
                logger_level="DEBUG", 
                handler_mode="CONSOLE"
            )
            config_logger.config_logger_elements()
        """
        level = self._get_logger_level()
        if level is None:
            # Get logger, ensure it's disabled or has no handlers
            logger = logging.getLogger(self.logger_name)
            logger.disabled = True 
            self.logger = logger
            return None # Return None if setup didn't happen

        logger = logging.getLogger(self.logger_name)
        logger.disabled = False # Ensure enabled if previously off

        logger.handlers.clear()

        if self.handler_mode in ['file', 'both']:
            filename = self._create_filename(self.log_directory)
        else:
            filename = None

        handlers = self._config_handlers(filename)

        logger.setLevel(level)

        formatter = logging.Formatter(self.format)
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Add NullHandler if user requested mode resulted in no actual handlers
        if not handlers and self.handler_mode not in [None, "off"]:
            logger.addHandler(logging.NullHandler())
            print(f"Warning: No handlers for mode '{self.handler_mode}', added NullHandler to '{self.logger_name}'")

        # Set propagate = False after adding handlers
        logger.propagate = False

        self.logger = logger
        print(f"Configured logger '{self.logger_name}'"
              f"(Level: {self.logger_level.upper()}," 
              f"Handlers: {[h.__class__.__name__ for h in logger.handlers]}," 
              f"Propagate: {logger.propagate})")

        return logger
