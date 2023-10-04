import functools

from ERKER2Phenopackets.src.logging_ import setup_logging
from loguru import logger


def log_args(func, raise_on_type_mismatch=False):
    """
    Decorator that logs the arguments of a function call and notifies when the
    function call started and finished.
    :param func: Callable to decorate
    :type func: Callable
    :param raise_on_type_mismatch: Whether to raise an exception if the actual
    type of an argument does not match the expected type
    :type raise_on_type_mismatch: bool
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
            if actual_type != arg_type:
                type_color = "\033[93m"
                if raise_on_type_mismatch:
                    raise TypeError(
                        f'Argument {i} of {func.__name__}() has type {actual_type} '
                        f'but expected type {arg_type}'
                    )
            else:
                type_color = ''

            log_message = (
                f'{func.__name__}():\t\t- arg {i}: {arg} '
                f'{type_color}(Type: {actual_type}, Expected Type: {arg_type})'
            )
            logger.trace(log_message)

        logger.trace(f'{func.__name__}():\tKeyword arguments:')
        for key, value in kwargs.items():
            kwarg_type = func.__annotations__.get(key, 'Any')
            actual_type = type(value)

            if actual_type != kwarg_type:
                type_color = "\033[93m"
                if raise_on_type_mismatch:
                    raise TypeError(
                        f'Keyword argument {key} of {func.__name__}() has type '
                        f'{actual_type} but expected type {kwarg_type}'
                    )
            else:
                type_color = ''
                
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
