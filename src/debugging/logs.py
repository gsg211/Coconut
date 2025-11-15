import logging as l
import defines as d

open(d.UTILS_LOG_PATH, 'w').close()

cl_logger = l.getLogger('CLIENT LOG: ')
cl_logger.setLevel(l.DEBUG)

sv_logger = l.getLogger('SERVER LOG: ')
sv_logger.setLevel(l.DEBUG)

utils_logger = l.getLogger('UTILS LOG:')
utils_logger.setLevel(l.DEBUG)

file_handler_sv = l.FileHandler(d.SERVER_LOG_PATH)
file_handler_cl = l.FileHandler(d.CLIENT_LOG_PATH)
file_handler_utils = l.FileHandler(d.UTILS_LOG_PATH)
console_handler = l.StreamHandler()



formatter = l.Formatter(
    "%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s"
)

file_handler_cl.setFormatter(formatter)
file_handler_sv.setFormatter(formatter)
file_handler_utils.setFormatter(formatter)
console_handler.setFormatter(formatter)

cl_logger.addHandler(file_handler_cl)
sv_logger.addHandler(file_handler_sv)
utils_logger.addHandler(file_handler_utils)

cl_logger.addHandler(console_handler)
sv_logger.addHandler(console_handler)
utils_logger.addHandler(console_handler)
