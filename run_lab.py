#!/usr/bin/env python3
"""Run all cases, verify codec round-trips, write RESULTS.md."""

import json
import sys
import traceback
import xmlrpc.client
from cases import CASES
from xmlrpc_dispatch import dispatch as D


_FAULT_CODE_TO_STRING = {
    1: "METHOD_NOT_FOUND",
    2: "ARITY_MISMATCH",
    3: "INVALID_PARAMS",
}


def safe_json_repr(obj):
    """JSON repr that survives NaN/inf – fall back to str."""
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)


def run_one(case):
    method = case["method"]
    encode_opts = case.get("encode_opts", {})
    allow_none = encode_opts.get("allow_none", False)
    use_builtin_types = encode_opts.get("use_builtin_types", True)

    # --- Encode stage ---
    if "raw_xml" in case:
        request_xml = case["raw_xml"]
        encode_exc_type = None
        encode_exc_msg = ""
    else:
        params = case["params"]
        try:
            request_xml = D.encode_request(method, params, allow_none=allow_none)
            encode_exc_type = None
            encode_exc_msg = ""
        except Exception as exc:
            return {
                "id": case["id"],
                "method": method,
                "classification": "encode_error",
                "encode_opts": encode_opts,
                "expected_stage": case["expected_stage"],
                "actual_stage": "encode_error",
                "expected_value": case.get("expected_value"),
                "expected_fault_code": case.get("expected_fault_code"),
                "actual_value": None,
                "actual_fault_code": None,
                "exc_type": type(exc).__name__,
                "exc_msg": str(exc),
                "observation": f"encode {type(exc).__name__}: {exc}",
                "pass": case["expected_stage"] == "encode_error",
            }

    # --- Dispatch ---
    stage, payload = D.dispatch_xml(request_xml, use_builtin_types=use_builtin_types)

    actual_value = None
    actual_fault_code = None
    exc_type = None
    exc_msg = ""
    observation = ""

    if stage == "parse_error":
        exc_type = type(payload).__name__
        exc_msg = str(payload)
        observation = f"parse {exc_type}: {exc_msg}"
    elif stage in ("method_fault", "arity_fault", "validation_fault"):
        actual_fault_code = payload
        observation = f"fault {payload} {_FAULT_CODE_TO_STRING.get(payload,'?')}"
    elif stage == "success":
        actual_value = payload
        observation = f"success value={safe_json_repr(payload)}"

    # --- Response round-trip verification ---
    roundtrip_ok = True
    roundtrip_note = ""
    if stage == "success":
        try:
            resp_xml = D.encode_response_success(payload, allow_none=allow_none)
            decoded, _ = xmlrpc.client.loads(resp_xml, use_builtin_types=use_builtin_types)
            decoded_value = decoded[0] if decoded else None
            if decoded_value != payload:
                roundtrip_ok = False
                roundtrip_note = f"response round-trip mismatch: {decoded_value!r} != {payload!r}"
        except Exception as exc:
            roundtrip_ok = False
            roundtrip_note = f"response encode/decode failed: {exc}"
    elif stage in ("method_fault", "arity_fault", "validation_fault"):
        try:
            resp_xml = D.encode_response_fault(payload, allow_none=allow_none)
            # xmlrpc.client.loads raises Fault – that's expected
            try:
                xmlrpc.client.loads(resp_xml, use_builtin_types=use_builtin_types)
                roundtrip_ok = False
                roundtrip_note = "fault response did not raise Fault on decode"
            except xmlrpc.client.Fault as f:
                if f.faultCode != payload or f.faultString != _FAULT_CODE_TO_STRING.get(payload, ""):
                    roundtrip_ok = False
                    roundtrip_note = f"fault round-trip mismatch: got {f.faultCode}/{f.faultString!r}"
        except Exception as exc:
            roundtrip_ok = False
            roundtrip_note = f"fault encode failed: {exc}"

    # --- Pass determination ---
    expected_stage = case["expected_stage"]
    stage_match = (stage == expected_stage)
    value_match = True
    if stage_match and stage == "success" and "expected_value" in case:
        value_match = (actual_value == case["expected_value"])
    if stage_match and stage in ("method_fault", "arity_fault", "validation_fault"):
        if "expected_fault_code" in case:
            value_match = (actual_fault_code == case["expected_fault_code"])

    passed = stage_match and value_match and roundtrip_ok
    if not roundtrip_ok:
        observation += f" | {roundtrip_note}"

    return {
        "id": case["id"],
        "method": method,
        "classification": stage,
        "encode_opts": encode_opts,
        "expected_stage": expected_stage,
        "actual_stage": stage,
        "expected_value": case.get("expected_value"),
        "expected_fault_code": case.get("expected_fault_code"),
        "actual_value": actual_value,
        "actual_fault_code": actual_fault_code,
        "exc_type": exc_type,
        "exc_msg": exc_msg,
        "observation": observation,
        "pass": passed,
    }


def main():
    rows = [run_one(c) for c in CASES]

    # Totals
    total = len(rows)
    passed = sum(1 for r in rows if r["pass"])
    failed = total - passed

    # Classification counts
    from collections import Counter
    counts = Counter(r["classification"] for r in rows)

    # Terminal output
    print(f"xmlrpc_dispatch_lab: {passed}/{total} passed")
    for r in rows:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  {status} {r['id']:25s} {r['actual_stage']:16s} {r['observation']}")
    print()
    print("Classification counts:")
    for k in sorted(counts):
        print(f"  {k:20s} {counts[k]}")
    print()

    # RESULTS.md
    with open("RESULTS.md", "w") as f:
        f.write("# RESULTS.md – python-xmlrpc-dispatch-lab\n\n")
        f.write(f"Passed: {passed}/{total}\n\n")
        f.write("| case | method | classification | expected | actual | result/fault | observation | pass |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            exp_val = safe_json_repr(r["expected_value"]) if r["expected_value"] is not None else (str(r["expected_fault_code"]) if r["expected_fault_code"] else "")
            act_val = safe_json_repr(r["actual_value"]) if r["actual_value"] is not None else (str(r["actual_fault_code"]) if r["actual_fault_code"] else (r["exc_type"] or ""))
            obs = r["observation"].replace("|", "\\|")
            f.write(f"| {r['id']} | {r['method']} | {r['classification']} | {r['expected_stage']} | {r['actual_stage']} | {act_val} | {obs} | {'yes' if r['pass'] else 'no'} |\n")
        f.write("\n## Classification totals\n\n")
        for k in sorted(counts):
            f.write(f"- {k}: {counts[k]}\n")
        f.write(f"\nTotal: {total}, Passed: {passed}, Failed: {failed}\n")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
