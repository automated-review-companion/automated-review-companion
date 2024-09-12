import logging

import colorlog


def Logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    formatter = colorlog.ColoredFormatter(
        fmt = '\033[97m[%(asctime)s] %(log_color)s%(levelname)s [%(name)s.%(funcName).30s()] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'blue',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler('server.log')
    fh.setLevel(logging.DEBUG)
    
    return logger