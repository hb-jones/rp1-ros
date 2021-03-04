import test_script

class test_class:
    def __init__(self):

        return
    def do_a_log(self,logger):
        logger.error("Error in a class")

import logging
import logging.config

logging.config.fileConfig('logging.conf')




logger = test_script.setup_logger()
logger.error("In other module")
e = test_class()
e.do_a_log(logger)