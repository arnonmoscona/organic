# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: free_range/core/client/tests/rpc_test_papi.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='free_range/core/client/tests/rpc_test_papi.proto',
  package='free_range.core.client.tests.papi.rpc_test_papi_pb2',
  syntax='proto3',
  serialized_pb=_b('\n0free_range/core/client/tests/rpc_test_papi.proto\x12\x33\x66ree_range.core.client.tests.papi.rpc_test_papi_pb2\"\x1e\n\x0bRpcRequestA\x12\x0f\n\x07request\x18\x01 \x01(\t\" \n\x0cRpcResponseA\x12\x10\n\x08response\x18\x01 \x01(\tb\x06proto3')
)




_RPCREQUESTA = _descriptor.Descriptor(
  name='RpcRequestA',
  full_name='free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcRequestA',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='request', full_name='free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcRequestA.request', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=105,
  serialized_end=135,
)


_RPCRESPONSEA = _descriptor.Descriptor(
  name='RpcResponseA',
  full_name='free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcResponseA',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='response', full_name='free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcResponseA.response', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=137,
  serialized_end=169,
)

DESCRIPTOR.message_types_by_name['RpcRequestA'] = _RPCREQUESTA
DESCRIPTOR.message_types_by_name['RpcResponseA'] = _RPCRESPONSEA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

RpcRequestA = _reflection.GeneratedProtocolMessageType('RpcRequestA', (_message.Message,), dict(
  DESCRIPTOR = _RPCREQUESTA,
  __module__ = 'free_range.core.client.tests.rpc_test_papi_pb2'
  # @@protoc_insertion_point(class_scope:free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcRequestA)
  ))
_sym_db.RegisterMessage(RpcRequestA)

RpcResponseA = _reflection.GeneratedProtocolMessageType('RpcResponseA', (_message.Message,), dict(
  DESCRIPTOR = _RPCRESPONSEA,
  __module__ = 'free_range.core.client.tests.rpc_test_papi_pb2'
  # @@protoc_insertion_point(class_scope:free_range.core.client.tests.papi.rpc_test_papi_pb2.RpcResponseA)
  ))
_sym_db.RegisterMessage(RpcResponseA)


# @@protoc_insertion_point(module_scope)
