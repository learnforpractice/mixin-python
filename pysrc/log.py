import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = '%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s'
    fmt = '%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s'
    #"%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logging.basicConfig(filename='logfile.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s')
formatter = CustomFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)

def get_logger(name):
    logger=logging.getLogger(name)
#    logger.addHandler(handler)
    return logger
