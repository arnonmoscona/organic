"""
Tests to validate generated protobuf code.
This file deviates from the convention of module per class/class per method
"""
import unittest

from free_range.core.client.tests.papi.rpc_test_papi_pb2 import (RpcRequestA,
                                                                 RpcResponseA)


class RpcAMessageTests(unittest.TestCase):
    def setUp(self):
        self.request = RpcRequestA()
        self.request.request = 'request 1'
        self.response = RpcResponseA()
        self.response.response = 'response 1'

    def test_request_is_initialized(self):
        self.assertTrue(self.request.IsInitialized())

    def test_response_is_initialized(self):
        self.assertTrue(self.response.IsInitialized())

    def test_request_serializes(self):
        serialized = self.request.SerializeToString()
        deserialized = RpcRequestA()
        deserialized.ParseFromString(serialized)
        self.assertEqual(self.request, deserialized)

    def test_response_serializes(self):
        serialized = self.response.SerializeToString()
        deserialized = RpcResponseA()
        deserialized.ParseFromString(serialized)
        self.assertEqual(self.response, deserialized)
