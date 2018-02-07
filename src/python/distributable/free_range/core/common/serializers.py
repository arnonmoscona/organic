"""
Serialization / deserialization related types and functions
"""
from abc import ABC, ABCMeta, abstractmethod

from free_range.core.common.dynamic import import_by_name
from free_range.core.common.exceptions import (InvalidArgumentError,
                                               InvalidStateError,
                                               SerializationError)


# OR-5: type hints


class Serializer(ABC):
    """
    Purely abstract base class for serializers.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def serialize(self, value):
        """
        Takes an instance of a serializable class and serializes it.
        :param value: The value to be serialized. Specific constraints for specific
                     serialization strategies
        :return: the serialized value. Typically a byte buffer or a text string.
        """
        return None

    @abstractmethod
    def deserialize(self, serialized_value):
        """
        Takes a serialized value and returns an instance.
        :param serialized_value: the value to "rehydrate"
        :return: an instance object. What class and how depends on specific implementations.
        """
        return None


class RpcProtobufSerializer:
    def __init__(self, argument_type_name, response_type_name):
        """
        A Protobuf 3 based serializer for RPC pattern endpoints. Knows about two types:
        request (argument) and response. Both must be Protobuf generated classes.
        The implementation does use duck typing, but the behavior is undefined if
        the types are not actually Protobuf 3 generated classes.
        The constructor does not validate that the names are valid or importable.
        :param argument_type_name: the request (argument) type.
               Expected to be a string whose value is the fully qualified name of
               the class. This is *not* the class itself.
        :param response_type_name: the response type.
               Expected to be a string whose value is the fully qualified name of
               the class. This is *not* the class itself.
        """
        self._argument_type_name = argument_type_name
        self._response_type_name = response_type_name
        self._imported = False
        self._argument_type = None
        self._response_type = None

    def import_types(self):
        """
        Dynamically imports the specified types. The serializer does not expect the types to be
        actually available on the Python path until this method is called. This is important,
        as the instance of the serializer may be created early in the application loading,
        while the path has not necessarily been set up yet and the classes may not yet be
        importable. Typiclly this will be called close to the time that actual serialization and
        deserialization is needed.
        :return: The serializer itself.
        """
        if self._imported:
            return self
        self._argument_type = _import_type_by_name(self._argument_type_name, None)
        self._response_type = _import_type_by_name(self._response_type_name, None)
        self._imported = True
        return self

    def argument_type(self, auto_import=True):
        """
        Returns the concrete type of the argument type.
        :param auto_import: if True then import_types() will be called if the classes have not
                           been imported yet.
        :return Class: the argument type (class)
        :raises InvalidStateError: if the classes were not imported and auto_import is False
        :raises NotFoundError: if could not find the class on the Python path
        :raises InvalidArgumentError: if the value of the class name is not valid.
        """
        self._require_import(self._argument_type_name, auto_import)
        return self._argument_type

    def response_type(self, auto_import=True):
        """
        Returns the concrete type of the response type.
        :param auto_import: if True then import_types() will be called if the classes have not
                           been imported yet.
        :return Class: the response type (class)
        :raises InvalidStateError: if the classes were not imported and auto_import is False
        :raises NotFoundError: if could not find the class on the Python path
        :raises InvalidArgumentError: if the value of the class name is not valid.
        """
        self._require_import(self._response_type_name, auto_import)
        return self._response_type

    def argument_type_serializer(self, auto_import=True):
        """
        Returns a concrete serializer for the argument type
        :param auto_import: if True and types were not yet imported, automatically imports them
        before constructing a Serializer.
        :return Serializer: a concrete implementation of the Serializer abstract class (interface)
        :raises InvalidStateError: if the classes were not imported and auto_import is False
        :raises NotFoundError: if could not find the class on the Python path
        :raises InvalidArgumentError: if the value of the class name is not valid.
        """
        self._require_import(self._argument_type_name, auto_import)
        return _SimpleProtobufTypeSerializer(self._argument_type, 'argument_type')

    def response_type_serializer(self, auto_import=True):
        """
        Returns a concrete serializer for the response type
        :param auto_import: if True and types were not yet imported, automatically imports them
        before constructing a Serializer.
        :return Serializer: a concrete implementation of the Serializer abstract class (interface)
        :raises InvalidStateError: if the classes were not imported and auto_import is False
        :raises NotFoundError: if could not find the class on the Python path
        :raises InvalidArgumentError: if the value of the class name is not valid.
        """
        self._require_import(self._response_type_name, auto_import)
        return _SimpleProtobufTypeSerializer(self._response_type, 'response_type')

    def _require_import(self, type_name, auto_import):
        if not self._imported:
            if auto_import:
                self.import_types()
            else:
                raise InvalidStateError(f'Attempt to retrieve type "{type_name}" before importing')


def _import_type_by_name(name, default_value):
    return import_by_name(name) if name is not None else default_value


class _SimpleProtobufTypeSerializer(Serializer):
    def __init__(self, clazz, role):
        self._role = role
        self._clazz = clazz

    def serialize(self, value):
        try:
            if self._clazz is None:
                raise InvalidArgumentError(f'No type associated with '
                                           f'{self._role} in this context - '
                                           f'cannot serialize')
            if value is None:
                return self._clazz().SerializeToString()
            if not isinstance(value, self._clazz):
                raise InvalidArgumentError(f'wrong type. Expected {type(self._clazz)}'
                                           f' but got {type(value)}')
            return value.SerializeToString()
        except InvalidArgumentError:
            raise
        except Exception as ex:
            raise SerializationError(msg=f'Error during serialize(): {type(ex)}: {ex}',
                                     caused_by=ex)

    def deserialize(self, serialized_value):
        try:
            if self._clazz is None:
                raise InvalidArgumentError(f'No type associated with '
                                           f'{self._role} in this context - '
                                           f'cannot deserialize')
            if not isinstance(serialized_value, bytes):
                raise InvalidArgumentError('desrialize only accepts byte arrays. '
                                           f'got {type(serialized_value)}')
            return_value = self._clazz()
            return_value.ParseFromString(serialized_value)
            return return_value
        except InvalidArgumentError:
            raise
        except Exception as ex:
            raise SerializationError(msg=f'Error during deserialize(): {type(ex)}: {ex}',
                                     caused_by=ex)
