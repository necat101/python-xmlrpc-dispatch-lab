#!/usr/bin/env python3
"""Independent unittest suite – does not import run_lab or cases."""

import hashlib
import inspect
import math
import unittest
import xmlrpc.client

from xmlrpc_dispatch import dispatch as D
from xmlrpc_dispatch import registry as R
from xmlrpc_dispatch.errors import InvalidParams


class TestDispatch(unittest.TestCase):

    def test_ping_roundtrip(self):
        xml = D.encode_request("system.ping", (42,), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "success")
        self.assertEqual(payload, "pong:42")

    def test_score_batch_ordering_tiebreak(self):
        items = [{"label": "b", "score": 2.0}, {"label": "a", "score": 2.0}, {"label": "c", "score": 1.0}]
        result = R.score_batch(items)
        self.assertEqual([r["label"] for r in result], ["a", "b", "c"])

    def test_score_batch_rejects_bool(self):
        with self.assertRaises(InvalidParams):
            R.score_batch([{"label": "x", "score": True}])

    def test_score_batch_rejects_nonfinite(self):
        for bad in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidParams):
                    R.score_batch([{"label": "x", "score": bad}])

    def test_unknown_method_fault_code_1(self):
        xml = D.encode_request("rank.nope", (), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "method_fault")
        self.assertEqual(payload, D.FAULT_METHOD_NOT_FOUND)

    def test_arity_fault_code_2(self):
        # missing
        xml = D.encode_request("rank.score_batch", (), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "arity_fault")
        self.assertEqual(payload, D.FAULT_ARITY_MISMATCH)
        # extra
        xml = D.encode_request("rank.score_batch", ([{"label": "a", "score": 1.0}], "extra"), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "arity_fault")
        self.assertEqual(payload, D.FAULT_ARITY_MISMATCH)

    def test_invalid_params_fault_code_3(self):
        xml = D.encode_request("rank.score_batch", ("not-a-list",), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "validation_fault")
        self.assertEqual(payload, D.FAULT_INVALID_PARAMS)

    def test_annotation_non_enforcement(self):
        """inspect.signature.bind checks shape, not annotated value types."""
        fn = R.score_batch
        sig = inspect.signature(fn)
        # Binding ("not-a-list",) to score_batch(items: list) succeeds –
        # annotations are not enforced at runtime
        bound = sig.bind("not-a-list")
        self.assertEqual(bound.arguments["items"], "not-a-list")
        # Explicit validation then rejects it
        with self.assertRaises(InvalidParams):
            fn(*bound.args)

    def test_binary_use_builtin_types(self):
        blob = b"\x00\xffAB"
        xml = D.encode_request("rank.describe_blob", (blob,), allow_none=False)
        # with use_builtin_types=True, Binary decodes to bytes
        stage, payload = D.dispatch_xml(xml, use_builtin_types=True)
        self.assertEqual(stage, "success")
        self.assertEqual(payload["len"], 4)
        self.assertEqual(payload["sha256"], hashlib.sha256(blob).hexdigest())
        # direct codec check
        params, method = xmlrpc.client.loads(xml, use_builtin_types=True)
        self.assertIsInstance(params[0], bytes)

    def test_none_allow_none_roundtrip(self):
        # allow_none=False → encode error
        with self.assertRaises(TypeError):
            D.encode_request("system.ping", (None,), allow_none=False)
        # allow_none=True → round-trips
        xml = D.encode_request("system.ping", (None,), allow_none=True)
        stage, payload = D.dispatch_xml(xml, use_builtin_types=True)
        self.assertEqual(stage, "success")
        self.assertEqual(payload, "pong:None")

    def test_int_boundary_encode_error(self):
        # in range: ok
        xml = D.encode_request("system.ping", (2147483647,), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "success")
        # out of range: Marshaller raises OverflowError
        with self.assertRaises(OverflowError):
            D.encode_request("system.ping", (2147483648,), allow_none=False)

    def test_malformed_xml(self):
        bad = b"<methodCall><methodName>rank.score_batch</methodName>"
        stage, payload = D.dispatch_xml(bad)
        self.assertEqual(stage, "parse_error")
        # payload is an exception, not a Fault
        self.assertIsInstance(payload, Exception)
        self.assertNotIsInstance(payload, xmlrpc.client.Fault)

    def test_fault_encode_decode(self):
        for code, expected_string in [(1, "METHOD_NOT_FOUND"), (2, "ARITY_MISMATCH"), (3, "INVALID_PARAMS")]:
            with self.subTest(code=code):
                resp_xml = D.encode_response_fault(code)
                with self.assertRaises(xmlrpc.client.Fault) as cm:
                    xmlrpc.client.loads(resp_xml)
                self.assertEqual(cm.exception.faultCode, code)
                self.assertEqual(cm.exception.faultString, expected_string)

    def test_dotted_method_name_registry(self):
        self.assertIn("rank.score_batch", R.REGISTRY)
        self.assertIs(R.REGISTRY["rank.score_batch"], R.score_batch)
        # unknown dotted name produces method_fault, not a crash
        xml = D.encode_request("rank.nope", (), allow_none=False)
        stage, payload = D.dispatch_xml(xml)
        self.assertEqual(stage, "method_fault")


if __name__ == "__main__":
    unittest.main(verbosity=2)
