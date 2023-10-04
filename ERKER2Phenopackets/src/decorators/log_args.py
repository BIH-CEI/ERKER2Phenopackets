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
            actual_type = type(arg)
            type_color = "\033[93m" if actual_type != arg_type else ''
            log_message = (
                f'{func.__name__}():\t\t- arg {i}: {arg} '
                f'{type_color}(Type: {actual_type}, Expected Type: {arg_type})'
            )
            logger.trace(log_message)

        logger.trace(f'{func.__name__}():\tKeyword arguments:')
        for key, value in kwargs.items():
            kwarg_type = func.__annotations__.get(key, 'Any')
            actual_type = type(value)
            type_color = "\033[93m" if actual_type != kwarg_type else ''
            log_message = (
                f'{func.__name__}():\t\t- {key}: {value} '
                f'{type_color}(Type: {actual_type}, Expected Type: {kwarg_type})'
            )
            logger.trace(log_message)

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
