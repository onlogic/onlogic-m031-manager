"""
Author: OnLogic
For:    K/HX-52x
Title:  

Description:
    TODO:

Usage:
    python main.py

NOTE: 
    - This program was tested on Python 3.13.0 and Python 3.12.4
    
    - CTRL+C can be used to exit the program.
"""

import timeit # Optional: measure time taken per sample
from DioHandler import DioHandler

def main():
    try:
        pass
    except KeyboardInterrupt:
        print("Operation terminated by user.")
    finally: 
        print("\033[93mExiting...\033[0m") 

if __name__ == "__main__":
    main()
