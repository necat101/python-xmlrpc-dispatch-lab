"""Method registry and implementations."""

import hashlib
import math
from .errors import InvalidParams


def ping(x):
    """system.ping – echo with a prefix, accepts any XML-RPC value."""
    return f"pong:{x}"


def score_batch(items: list):
    """rank.score_batch – accept a list of {label, score} structs, return ranked list.

    Validation (explicit, annotations are NOT enforced at runtime):
    - items must be a list
    - each element must be a dict with 'label' (str) and 'score' (int/float, not bool, finite)
    - returns list sorted by descending score, then ascending label
    """
    if not isinstance(items, list):
        raise InvalidParams("items must be list")
    out = []
    for i, e in enumerate(items):
        if not isinstance(e, dict):
            raise InvalidParams(f"element {i} not a dict")
        if "label" not in e or "score" not in e:
            raise InvalidParams(f"element {i} missing label/score")
        label = e["label"]
        score = e["score"]
        if not isinstance(label, str):
            raise InvalidParams(f"element {i} label must be str")
        # bool is subclass of int in Python – reject explicitly
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise InvalidParams(f"element {i} score must be numeric, not bool")
        if isinstance(score, float) and not math.isfinite(score):
            raise InvalidParams(f"element {i} score must be finite")
        out.append({"label": label, "score": float(score)})
    out.sort(key=lambda r: (-r["score"], r["label"]))
    return out


def describe_blob(blob: bytes):
    """rank.describe_blob – accept binary data, return len + sha256."""
    if not isinstance(blob, bytes):
        raise InvalidParams("blob must be bytes")
    return {"len": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}


# Explicit registry: dotted RPC name -> callable
REGISTRY = {
    "system.ping": ping,
    "rank.score_batch": score_batch,
    "rank.describe_blob": describe_blob,
}
