# RESULTS.md – python-xmlrpc-dispatch-lab

Passed: 14/14

| case | method | classification | expected | actual | result/fault | observation | pass |
|---|---|---|---|---|---|---|---|
| c01_valid | rank.score_batch | success | success | success | [{"label": "a", "score": 2.0}, {"label": "b", "score": 2.0}, {"label": "c", "score": 1.0}] | success value=[{"label": "a", "score": 2.0}, {"label": "b", "score": 2.0}, {"label": "c", "score": 1.0}] | yes |
| c02_ties | rank.score_batch | success | success | success | [{"label": "a", "score": 5.0}, {"label": "m", "score": 5.0}, {"label": "z", "score": 5.0}] | success value=[{"label": "a", "score": 5.0}, {"label": "m", "score": 5.0}, {"label": "z", "score": 5.0}] | yes |
| c03_unknown_method | rank.nope | method_fault | method_fault | method_fault | 1 | fault 1 METHOD_NOT_FOUND | yes |
| c04_missing_arg | rank.score_batch | arity_fault | arity_fault | arity_fault | 2 | fault 2 ARITY_MISMATCH | yes |
| c05_extra_arg | rank.score_batch | arity_fault | arity_fault | arity_fault | 2 | fault 2 ARITY_MISMATCH | yes |
| c06_wrong_param_type | rank.score_batch | validation_fault | validation_fault | validation_fault | 3 | fault 3 INVALID_PARAMS | yes |
| c07_malformed_xml | rank.score_batch | parse_error | parse_error | parse_error | ExpatError | parse ExpatError: no element found: line 1, column 53 | yes |
| c08_none_rejected | rank.score_batch | encode_error | encode_error | encode_error | TypeError | encode TypeError: cannot marshal None unless allow_none is enabled | yes |
| c09_none_allowed | system.ping | success | success | success | "pong:None" | success value="pong:None" | yes |
| c10_int_in_range | system.ping | success | success | success | "pong:2147483647" | success value="pong:2147483647" | yes |
| c11_int_out_of_range | system.ping | encode_error | encode_error | encode_error | OverflowError | encode OverflowError: int exceeds XML-RPC limits | yes |
| c12_binary_rt | rank.describe_blob | success | success | success | {"len": 4, "sha256": "49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5"} | success value={"len": 4, "sha256": "49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5"} | yes |
| c13_bool_rejected_score | rank.score_batch | validation_fault | validation_fault | validation_fault | 3 | fault 3 INVALID_PARAMS | yes |
| c14_nonfinite_rejected_score | rank.score_batch | validation_fault | validation_fault | validation_fault | 3 | fault 3 INVALID_PARAMS | yes |

## Classification totals

- arity_fault: 2
- encode_error: 2
- method_fault: 1
- parse_error: 1
- success: 5
- validation_fault: 3

Total: 14, Passed: 14, Failed: 0
