import warnings
import functools
from loguru import logger


def deprecated(reason=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning(f'DeprecationWarning: {func.__name__} is deprecated.' 
                           f' {reason}')
            warnings.warn(f'{func.__name__} is deprecated. {reason}', 
                          category=DeprecationWarning)
            return func(*args, **kwargs)
        return wrapper
    return decorator
