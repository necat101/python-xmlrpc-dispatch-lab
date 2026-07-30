"""Fixed case manifest for python-xmlrpc-dispatch-lab.

Every rpc call is represented as an exact tuple of positional arguments,
matching xmlrpc.client.dumps() expectations.
"""

# Blob for c12_binary_rt: b"\x00\xffAB"
# sha256 = hashlib.sha256(b"\x00\xffAB").hexdigest()
#        = "49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5"

CASES = [
    {
        "id": "c01_valid",
        "method": "rank.score_batch",
        "params": ([{"label": "b", "score": 2.0}, {"label": "a", "score": 2.0}, {"label": "c", "score": 1.0}],),
        "encode_opts": {},
        "expected_stage": "success",
        "expected_value": [{"label": "a", "score": 2.0}, {"label": "b", "score": 2.0}, {"label": "c", "score": 1.0}],
    },
    {
        "id": "c02_ties",
        "method": "rank.score_batch",
        "params": ([{"label": "z", "score": 5.0}, {"label": "a", "score": 5.0}, {"label": "m", "score": 5.0}],),
        "encode_opts": {},
        "expected_stage": "success",
        "expected_value": [{"label": "a", "score": 5.0}, {"label": "m", "score": 5.0}, {"label": "z", "score": 5.0}],
    },
    {
        "id": "c03_unknown_method",
        "method": "rank.nope",
        "params": (),
        "encode_opts": {},
        "expected_stage": "method_fault",
        "expected_fault_code": 1,
    },
    {
        "id": "c04_missing_arg",
        "method": "rank.score_batch",
        "params": (),
        "encode_opts": {},
        "expected_stage": "arity_fault",
        "expected_fault_code": 2,
    },
    {
        "id": "c05_extra_arg",
        "method": "rank.score_batch",
        "params": ([{"label": "a", "score": 1.0}], "extra"),
        "encode_opts": {},
        "expected_stage": "arity_fault",
        "expected_fault_code": 2,
    },
    {
        "id": "c06_wrong_param_type",
        "method": "rank.score_batch",
        "params": ("not-a-list",),
        "encode_opts": {},
        "expected_stage": "validation_fault",
        "expected_fault_code": 3,
    },
    {
        "id": "c07_malformed_xml",
        "method": "rank.score_batch",
        "raw_xml": b"<methodCall><methodName>rank.score_batch</methodName>",
        "encode_opts": {},
        "expected_stage": "parse_error",
    },
    {
        "id": "c08_none_rejected",
        "method": "rank.score_batch",
        "params": (None,),
        "encode_opts": {"allow_none": False},
        "expected_stage": "encode_error",
    },
    {
        "id": "c09_none_allowed",
        "method": "system.ping",
        "params": (None,),
        "encode_opts": {"allow_none": True},
        "expected_stage": "success",
        "expected_value": "pong:None",
    },
    {
        "id": "c10_int_in_range",
        "method": "system.ping",
        "params": (2147483647,),
        "encode_opts": {},
        "expected_stage": "success",
        "expected_value": "pong:2147483647",
    },
    {
        "id": "c11_int_out_of_range",
        "method": "system.ping",
        "params": (2147483648,),
        "encode_opts": {},
        "expected_stage": "encode_error",
    },
    {
        "id": "c12_binary_rt",
        "method": "rank.describe_blob",
        "params": (b"\x00\xffAB",),
        "encode_opts": {"use_builtin_types": True},
        "expected_stage": "success",
        "expected_value": {"len": 4, "sha256": "49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5"},
    },
    {
        "id": "c13_bool_rejected_score",
        "method": "rank.score_batch",
        "params": ([{"label": "x", "score": True}],),
        "encode_opts": {},
        "expected_stage": "validation_fault",
        "expected_fault_code": 3,
    },
    {
        "id": "c14_nonfinite_rejected_score",
        "method": "rank.score_batch",
        "params": ([{"label": "x", "score": float("nan")}],),
        "encode_opts": {},
        "expected_stage": "validation_fault",
        "expected_fault_code": 3,
    },
]

# Sanity: unique ids, recognized classifications
_ALLOWED_STAGES = {"success", "encode_error", "parse_error", "method_fault", "arity_fault", "validation_fault"}
_ids = [c["id"] for c in CASES]
assert len(_ids) == len(set(_ids)), "duplicate case ids"
for c in CASES:
    assert c["expected_stage"] in _ALLOWED_STAGES, f"{c['id']} bad stage"
