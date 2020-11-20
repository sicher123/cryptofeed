'''
Copyright (C) 2017-2020  Bryant Moscon - bmoscon@gmail.com

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
import os
import logging


FORMAT = logging.Formatter('%(asctime)-15s : %(levelname)s : %(message)s')
if os.name == "nt":
    PATH = os.path.abspath(r"C:/Desktop")
elif os.name == "posix":
    PATH = "/log"

def get_logger(name, filename, level=logging.WARNING):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    stream = logging.StreamHandler()
    stream.setFormatter(FORMAT)
    logger.addHandler(stream)

    fh = logging.FileHandler(PATH + "/" + filename)
    fh.setFormatter(FORMAT)
    logger.addHandler(fh)
    logger.propagate = False
    return logger
