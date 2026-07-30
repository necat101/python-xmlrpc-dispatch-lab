"""XML-RPC codec adapter and dispatcher. No sockets, no HTTP server."""

import inspect
import xmlrpc.client
from .registry import REGISTRY
from .errors import InvalidParams


# Fault codes
FAULT_METHOD_NOT_FOUND = 1
FAULT_ARITY_MISMATCH = 2
FAULT_INVALID_PARAMS = 3

_FAULT_STRINGS = {
    FAULT_METHOD_NOT_FOUND: "METHOD_NOT_FOUND",
    FAULT_ARITY_MISMATCH: "ARITY_MISMATCH",
    FAULT_INVALID_PARAMS: "INVALID_PARAMS",
}


def encode_request(method_name: str, params: tuple, allow_none: bool = False) -> bytes:
    """Encode an XML-RPC methodCall. params must be a tuple."""
    return xmlrpc.client.dumps(params, methodname=method_name, allow_none=allow_none).encode("utf-8")


def encode_response_success(result, allow_none: bool = False) -> bytes:
    """Encode exactly one return value as a methodResponse."""
    xml = xmlrpc.client.dumps((result,), methodresponse=True, allow_none=allow_none)
    return xml.encode("utf-8")


def encode_response_fault(code: int, allow_none: bool = False) -> bytes:
    """Encode an xmlrpc.client.Fault response."""
    fault_string = _FAULT_STRINGS.get(code, "FAULT")
    fault = xmlrpc.client.Fault(code, fault_string)
    xml = xmlrpc.client.dumps(fault, allow_none=allow_none)
    return xml.encode("utf-8")


def dispatch_xml(request_xml: bytes, *, use_builtin_types: bool = True):
    """Dispatch a methodCall XML document locally.

    Returns: (stage, payload)
      stage is one of: "success", "method_fault", "arity_fault", "validation_fault", "parse_error"
      payload is the decoded result / fault code / exception info

    This function never raises for application faults – they are returned as
    ("method_fault"|"arity_fault"|"validation_fault", code).
    Parse errors are returned as ("parse_error", exc).
    """
    # --- Parse ---
    try:
        params, method_name = xmlrpc.client.loads(
            request_xml, use_builtin_types=use_builtin_types
        )
    except Exception as exc:
        return "parse_error", exc

    # --- Method lookup ---
    fn = REGISTRY.get(method_name)
    if fn is None:
        return "method_fault", FAULT_METHOD_NOT_FOUND

    # --- Arity binding ---
    try:
        inspect.signature(fn).bind(*params)
    except TypeError as exc:
        return "arity_fault", FAULT_ARITY_MISMATCH

    # --- Value validation / call ---
    try:
        result = fn(*params)
    except InvalidParams:
        return "validation_fault", FAULT_INVALID_PARAMS

    return "success", result
