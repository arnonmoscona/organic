"""
Endpoint related types
"""
import json
import logging
import re
from json import JSONDecodeError

from free_range.core.common.decorators import public_interface
from free_range.core.common.exceptions import InvalidArgumentError

PATTERN_RPC = 'RPC'

logger = logging.getLogger('free_range.core.common.endpoints')

KEY_RETURN_TYPE = 'returnType'
KEY_CALLABLE = 'callable'
KEY_ARGUMENT_TYPE = 'argumentType'


class Endpoint:
    """
    An endpoint is a specifier of an interaction node with a known behavior. For instance: an RPC
    endpoint, which is a function that can be either local or remote, over the network or in
    the stack.

    An Endpoint does not specify the location of the interaction point or the route to it. That
    is the role of the routing component and its associated configuration. In the absence of
    routing an endpoint is assumed to be on the stack, meaning that it can be translated
    directly into some Python object. What kind of Python object depends on the kind of endpoint
    involved. For instance, an RPC endpoint translates by default to a function that can be
    locally imported.

    Defaults can usually be overridden by configuration.

    In order to use endpoints in any way other than in-process defaults, a router is needed.

    Endpoints can always be constructed from a string and can be translated back into exactly the
    same string.

    The root Endpoint class is just a marker interface allowing easy object oriented
    grouping and global identification of endpoints. It has no other real use.
    """

    @public_interface
    def __init__(self, endpoint_string):
        self._string_repr = None
        self._validate_repr(str(endpoint_string))

    def __str__(self):
        return self._string_repr

    @property
    def pattern(self):
        return None

    def _validate_repr(self, endpoint_string):
        raise InvalidArgumentError('The base Endpoint class is never valid.')


# OR-5: type hints
class RpcEndpoint(Endpoint):
    option_strict = False

    @public_interface
    def __init__(self, string_repr):
        """
        Creates an RPC endpoint reference. An RPC endpoint reference has three parts. There is a
        "fully qualified symbol" for the "function". This refers to a function that takes up to
        one typed argument and may return a single typed response.

        The second part is an optional argument type, which is also a "fully qualified symbol".
        If not present, then the function is assumed to take no arguments. If present, then this
        is the type of the argument it takes. This type should be serializable using the
        serializer in use.

        The third part is the type of the return type. If not present then the function is
        assumed to return None. If present then this is the "fully qualified symbol" of the
        return type, which must also be serializable using the same serializer used for the
        argument.

        A "fully qualified symbol" is a string representation of a type or function. The
        simplest way to think about it is simply the way you would reference the symbol in a
        python import statement. For example "my.package.function_name". As long as one is in a
        pure Python world these are easy to understand. Note though that being a distributed
        system, the "other side" of the communications may not be written in Python and there
        this convention may not directly map quite as simply.

        Both the argument type and the return type must exist in the local interpreter such that
        they can be locally imported. That is to say that if the return type reference is
        "my.package.ReturnType" then you must be able to write the Python code
        "from my.package import ReturnType" and that the serializer must be able to
        use this type to serialize and deserialize instances. So there would be additional
        serializer type based constraints.

        In contrast, the function reference does not have to exist locally. It may actually only
        exist on some remote system. However if you want to have actual running code for local
        debugging with a local transport, then the actual function that is referenced by this
        string will be invoked. Naturally, it does not have to be strictly a function as any
        conforming callable would do.

        The class does not fully validate these constraints so technically, the references don't
        need to be importable at the time the endpoint reference is created. They only need to be
        importable at the time of use. Some validation is done. The default validation is quite
        loose, and only parses the string to separate out the three parts. The string must be of
        the form (JSON):
        {"callable": "func.ref", "argumentType": "arg.ref1", "returnType": "arg.ref2"}

        The "fully qualified symbol" strings may not include any of the following:
        '(', ')', ':' and whitespace. No other validation is performed by the default validation.
        A stricter validation can be chosen by setting the class level strict validation option.
        This is done by calling set_option_strict(True) prior to creating an endpoint reference.
        :param string_repr: see description above.
        """

        super().__init__(string_repr)

    def _validate_repr(self, endpoint_string):
        self._parse_endpoint(endpoint_string)
        if RpcEndpoint.option_strict:
            self._validate_endpoint_strict(endpoint_string)
        self._make_string_repr()
        # by default there's nothing really to validate

    @classmethod
    @public_interface
    def set_option_strict(cls, strict):
        """
        Set strict validation for the string representation of the endpoint.
        If strict validation is False (the default), then only basic validation is done.
        With strict validation, the string is taken as a period delimited string, with each of
        the components matching [A-Za-z_]+[A-Za-z0-9_]*

        Note that this does not represent an exact match to Python's package and function name
        validation, nor does it check in any way whether or not the string represents anything
        that actually exists, as it may very well not exist locally.
        :param strict: whether or not the class level configuration option_strict should be True
               or False
        """
        RpcEndpoint.option_strict = bool(strict)

    def _make_string_repr(self):
        self._string_repr = f'RpcEndpoint<{self._function_reference}>'

    def _parse_endpoint(self, endpoint_string):
        # OR-6: identify that it's RPC in the JSON {"pattern": "RPC", "spec": {...}}
        # sample = '{"callable": "func.ref", "argumentType": "arg.ref1", "returnType": "arg.ref2"}'
        try:
            parsed = json.loads(endpoint_string)
        except (TypeError, JSONDecodeError) as cause:
            raise InvalidArgumentError('Error parsing endpoint reference: {cause}', caused_by=cause)

        keys = set(parsed.keys())
        allowed_keys = {KEY_ARGUMENT_TYPE, KEY_CALLABLE, KEY_RETURN_TYPE}
        unknown_keys = allowed_keys - keys
        if len(unknown_keys) > 0:
            logger.debug(f'Unrecognized keys in endpoint reference: {unknown_keys}')

        self._function_reference = parsed.get(KEY_CALLABLE, None)
        self._argument_type_reference = parsed.get(KEY_ARGUMENT_TYPE, None)
        self._returnType_reference = parsed.get(KEY_RETURN_TYPE, None)

        if self._function_reference is None:
            raise InvalidArgumentError('A function reference is required for an RPC endpoint')

    def _validate_endpoint_strict(self, endpoint_string):
        # no surrounding whitespace
        # we do not check whether types are importable at this point
        for item in [
            (self._function_reference, 'function'),
            (self._argument_type_reference, 'argument type'),
            (self._returnType_reference, 'return type'),
        ]:
            reference = item[0]
            names = reference.split('.') if reference else []
            for name in names:
                self._validate_name_string_strict(name, f'"{name}" in "{item[1]}" reference')

    def _validate_name_string_strict(self, item, descr):
        if item is None:
            return
        if item != item.strip():
            raise InvalidArgumentError(f'{descr} may not have surrounding whitespace')

        regexp = '^[A-Za-z_]+[A-Za-z0-9_]*$'
        if not re.match(regexp, item):
            raise InvalidArgumentError(f'does not match "{regexp}"')

    @property
    @public_interface
    def function_reference_string(self):
        return self._function_reference

    @property
    @public_interface
    def argument_type_reference_string(self):
        return self._argument_type_reference

    @property
    @public_interface
    def return_type_reference_string(self):
        return self._returnType_reference

    @property
    @public_interface
    def pattern(self):
        return PATTERN_RPC

    @property
    @public_interface
    def unique_reference(self):
        return f'{self.pattern}:{self.function_reference_string}'
