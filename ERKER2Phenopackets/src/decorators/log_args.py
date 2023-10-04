import functools

from ERKER2Phenopackets.src.logging_ import setup_logging
from loguru import logger


def log_args(func):
    """
    Decorator that logs the arguments of a function call and notifies when the
    function call started and finished.
    :param func: Callable to decorate
    :type func: Callable
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.trace(f'Method {func.__name__}() started')

        logger.trace(f'{func.__name__}():\tArguments:')
        for i, (arg, arg_type) in enumerate(
                zip(args, func.__annotations__.values()),
                1
        ):
            logger.trace(f'{func.__name__}():\t\t- arg {i}: {arg} (Type: {type(arg)},'
                         f'Expected Type: {arg_type})')

        logger.trace(f'{func.__name__}():\tKeyword arguments:')
        for key, value in kwargs.items():
            kwarg_type = func.__annotations__.get(key, 'Any')
            logger.trace(f'{func.__name__}():\t\t- {key}: {value} (Type: {type(value)},'
                         f' Expected Type: {kwarg_type})')

        result = func(*args, **kwargs)

        logger.trace(f'Method {func.__name__}() finished')

        return result

    return wrapper


@log_args
def foo(a: int, b: str, c: float):
    print(f'a: {a}, b: {b}, c: {c}')


if __name__ == '__main__':
    setup_logging(level='TRACE')
    foo(1, b=2, c=3)
