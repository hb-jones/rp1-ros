import logging
import logging.handlers
import os
import sys



def setup_logger(): #TODO move this within API somewhere
    #logging.basicConfig(filename="log/yourapp.log", encoding='utf-8', level=logging.DEBUG, style = '{', format='{levelname}:{name}:{relativeCreated:0.1f}:{message}')
    logger = logging.getLogger(__name__)
    std_formatter = logging.Formatter(fmt='{asctime}  -  {levelname}:{module}:{funcName}:{message}',style='{')

    console_handler = logging.StreamHandler(stream= sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(std_formatter)
    logger.addHandler(console_handler)

    logger.warning("warn")
    logger.debug('test')
    return logger

