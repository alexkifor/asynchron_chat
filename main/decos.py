import sys
import logging
import inspect



def log(func_to_log):
    def wrapper(*args, **kwargs):
        func_out = func_to_log(*args, **kwargs)
        data = sys.argv[0].split('.')[0]
        LOG = logging.getLogger(f'{data}')
        LOG.debug(f'A function {func_to_log.__name__} was called with parameters {args}, {kwargs} from the function {inspect.stack()[1][3]}', stacklevel=2)
        return func_out
    return wrapper