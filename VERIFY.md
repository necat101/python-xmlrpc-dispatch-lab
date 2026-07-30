# VERIFY.md – python-xmlrpc-dispatch-lab

Fresh-clone verification of commit a1c2793e7608930378ad0d1f7be8226cb3166554

## Clone

```
$ git clone https://github.com/necat101/python-xmlrpc-dispatch-lab.git verify-xmlrpc
Cloning into 'verify-xmlrpc'...
$ cd verify-xmlrpc
$ git rev-parse HEAD
a1c2793e7608930378ad0d1f7be8226cb3166554
```

## Python version

```
Python 3.12.3
```

## Compile

```
$ python3 -m py_compile $(find . -name "*.py")
compile_exit=0
```

## Runner

```
$ python3 run_lab.py
xmlrpc_dispatch_lab: 14/14 passed
  PASS c01_valid                 success          success value=[{"label": "a", "score": 2.0}, {"label": "b", "score": 2.0}, {"label": "c", "score": 1.0}]
  PASS c02_ties                  success          success value=[{"label": "a", "score": 5.0}, {"label": "m", "score": 5.0}, {"label": "z", "score": 5.0}]
  PASS c03_unknown_method        method_fault     fault 1 METHOD_NOT_FOUND
  PASS c04_missing_arg           arity_fault      fault 2 ARITY_MISMATCH
  PASS c05_extra_arg             arity_fault      fault 2 ARITY_MISMATCH
  PASS c06_wrong_param_type      validation_fault fault 3 INVALID_PARAMS
  PASS c07_malformed_xml         parse_error      parse ExpatError: no element found: line 1, column 53
  PASS c08_none_rejected         encode_error     encode TypeError: cannot marshal None unless allow_none is enabled
  PASS c09_none_allowed          success          success value="pong:None"
  PASS c10_int_in_range          success          success value="pong:2147483647"
  PASS c11_int_out_of_range      encode_error     encode OverflowError: int exceeds XML-RPC limits
  PASS c12_binary_rt             success          success value={"len": 4, "sha256": "49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5"}
  PASS c13_bool_rejected_score   validation_fault fault 3 INVALID_PARAMS
  PASS c14_nonfinite_rejected_score validation_fault fault 3 INVALID_PARAMS

Classification counts:
  arity_fault          2
  encode_error         2
  method_fault         1
  parse_error          1
  success              5
  validation_fault     3

runner_exit=0
```

Runner totals: 14 passed / 14 total, 0 failed.

Classification totals:
- success: 5
- encode_error: 2
- parse_error: 1
- method_fault: 1
- arity_fault: 2
- validation_fault: 3

## Unittest

```
$ python3 -m unittest -v test_dispatch.py
test_annotation_non_enforcement (test_dispatch.TestDispatch.test_annotation_non_enforcement)
inspect.signature.bind checks shape, not annotated value types. ... ok
test_arity_fault_code_2 (test_dispatch.TestDispatch.test_arity_fault_code_2) ... ok
test_binary_use_builtin_types (test_dispatch.TestDispatch.test_binary_use_builtin_types) ... ok
test_dotted_method_name_registry (test_dispatch.TestDispatch.test_dotted_method_name_registry) ... ok
test_fault_encode_decode (test_dispatch.TestDispatch.test_fault_encode_decode) ... ok
test_int_boundary_encode_error (test_dispatch.TestDispatch.test_int_boundary_encode_error) ... ok
test_invalid_params_fault_code_3 (test_dispatch.TestDispatch.test_invalid_params_fault_code_3) ... ok
test_malformed_xml (test_dispatch.TestDispatch.test_malformed_xml) ... ok
test_none_allow_none_roundtrip (test_dispatch.TestDispatch.test_none_allow_none_roundtrip) ... ok
test_ping_roundtrip (test_dispatch.TestDispatch.test_ping_roundtrip) ... ok
test_score_batch_ordering_tiebreak (test_dispatch.TestDispatch.test_score_batch_ordering_tiebreak) ... ok
test_score_batch_rejects_bool (test_dispatch.TestDispatch.test_score_batch_rejects_bool) ... ok
test_score_batch_rejects_nonfinite (test_dispatch.TestDispatch.test_score_batch_rejects_nonfinite) ... ok
test_unknown_method_fault_code_1 (test_dispatch.TestDispatch.test_unknown_method_fault_code_1) ... ok

----------------------------------------------------------------------
Ran 14 tests in 0.003s

OK
unittest_exit=0
```

Unittest count: 14, passed: 14, failed: 0.

## Regenerated RESULTS.md comparison

```
$ python3 run_lab.py >/dev/null && git diff --exit-code -- RESULTS.md
diff_exit=0
```

Generated RESULTS.md is identical to committed version.

## Working tree

```
$ git status --short
(clean)
```

## Summary

- Implementation SHA: a1c2793e7608930378ad0d1f7be8226cb3166554
- Python: 3.12.3
- py_compile: exit 0
- Runner: 14/14 passed, exit 0
- Unittest: 14/14 passed, exit 0
- RESULTS.md regeneration: identical (diff exit 0)
- Working tree: clean
- Failures: 0
- Skips: 0
- Wall time: <2s

Verification: PASS
