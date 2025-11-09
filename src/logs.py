import logging as l

cl_logger = l.getLogger('CLIENT LOGG: ')
cl_logger.setLevel(l.DEBUG)

sv_logger = l.getLogger('SERVER LOG: ')
sv_logger.setLevel(l.DEBUG)

file_handler_sv = l.FileHandler('../logs/sv_log.log')
file_handler_cl = l.FileHandler('../logs/cl_log.log')
console_handler = l.StreamHandler()



formatter = l.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

file_handler_cl.setFormatter(formatter)
file_handler_sv.setFormatter(formatter)
console_handler.setFormatter(formatter)

cl_logger.addHandler(file_handler_cl)
sv_logger.addHandler(file_handler_sv)

cl_logger.addHandler(console_handler)
sv_logger.addHandler(console_handler)
