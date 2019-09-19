import logging


def init():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    synch_logger = logging.getLogger("synch")
    synch_logger.setLevel(logging.DEBUG)
    synch_fh = logging.FileHandler('synch.log')
    synch_fh.setLevel(logging.DEBUG)
    synch_fh.setFormatter(formatter)
    synch_logger.addHandler(synch_fh)

    debug_logger = logging.getLogger('debug')
    debug_logger.setLevel(logging.DEBUG)
    debug_fh = logging.FileHandler('debug.log')
    debug_fh.setLevel(logging.DEBUG)
    debug_fh.setFormatter(formatter)
    debug_logger.addHandler(debug_fh)
