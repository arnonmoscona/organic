"""
Common decorators used in implementation
"""
from functools import wraps


def public_interface(f):
    """
    Used to declare public interfaces whether they are functions, classes, or methods.
    At the very least allows you to easily find them and list them.
    Also can verify some of the basic constraints on conforming public interfaces.
    :param f: the callable that is declared a public interface.
    :return: a wrapper that executed it.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # OR-7: declaring on some classes breaks code
        # OR-8: validate that f conforms to public interface requirements (cache result)
        # OR-8: if f is a class then apply public class requirements
        # OR-8: check that the package exports f (unless f is a method)
        # OR-9: support listing all public interfaces
        # OR-10: support tracing public interfaces
        # OR-10: support timing public interfaces
        return f(*args, **kwargs)

    return wrapper
