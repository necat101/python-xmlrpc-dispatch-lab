# python-xmlrpc-dispatch-lab

A small deterministic Python standard-library correctness lab modeling a tiny ML-adjacent scoring service as an in-memory XML-RPC boundary. No sockets, no HTTP server, no network requests.

The lab focuses on how the XML-RPC codec, method dispatch, and application validation interact, not on model quality.

## Scope

Four narrow questions, using only the Python standard library (`xmlrpc.client`, `inspect`, explicit registry):

1. **Dotted method names**: `rank.score_batch` maps to one registered callable; an unknown method produces a deterministic application fault.
2. **Positional binding vs type validation**: `inspect.signature(fn).bind(*params)` detects missing/extra arguments, but annotations alone do **not** enforce runtime value types – the service still needs explicit validation.
3. **XML-RPC value model effects**: default rejection of `None`, opt-in `allow_none` extension, standard 32-bit signed integer boundary, binary values decoded with `use_builtin_types=True`.
4. **Observable stage separation**: a malformed XML request, an application-level fault, and a successful response are observably different stages and should not be collapsed into one generic failure.

## Procedures

- `system.ping(x)` – echo with prefix, accepts any XML-RPC value
- `rank.score_batch(items)` – accept list of `{label, score}` structs, reject booleans and non-finite numeric scores, return deterministic ranking by descending score with alphabetical label tie-break
- `rank.describe_blob(blob)` – accept binary data, return `{"len": N, "sha256": "…"}`

## Cases (14)

| id | method | params | expected |
|---|---|---|---|
| c01_valid | `rank.score_batch` | `([{"label":"b","score":2.0},{"label":"a","score":2.0},{"label":"c","score":1.0}],)` | success, ranked a,b,c |
| c02_ties | `rank.score_batch` | `([{"label":"z","score":5.0},{"label":"a","score":5.0},{"label":"m","score":5.0}],)` | success, ranked a,m,z |
| c03_unknown_method | `rank.nope` | `()` | method_fault code 1 |
| c04_missing_arg | `rank.score_batch` | `()` | arity_fault code 2 |
| c05_extra_arg | `rank.score_batch` | `([{"label":"a","score":1.0}], "extra")` | arity_fault code 2 |
| c06_wrong_param_type | `rank.score_batch` | `("not-a-list",)` | validation_fault code 3 |
| c07_malformed_xml | `rank.score_batch` | raw truncated XML | parse_error |
| c08_none_rejected | `rank.score_batch` | `(None,)` allow_none=False | encode_error |
| c09_none_allowed | `system.ping` | `(None,)` allow_none=True | success `"pong:None"` |
| c10_int_in_range | `system.ping` | `(2147483647,)` | success |
| c11_int_out_of_range | `system.ping` | `(2147483648,)` | encode_error (OverflowError) |
| c12_binary_rt | `rank.describe_blob` | `(b"\x00\xffAB",)` use_builtin_types=True | success `len=4, sha256=49fd534fea14753447a1931542d9d58744a75810b88718eadc4ccded926317b5` |
| c13_bool_rejected_score | `rank.score_batch` | `([{"label":"x","score":True}],)` | validation_fault code 3 |
| c14_nonfinite_rejected_score | `rank.score_batch` | `([{"label":"x","score":float("nan")}],)` | validation_fault code 3 |

Result taxonomy: `success`, `encode_error`, `parse_error`, `method_fault`, `arity_fault`, `validation_fault`.

## Evidence sources

Evidence is kept separate – do not conflate these categories:

### Hacker News opinions

From [HN #32116877 – XML-RPC Specification (1999)](https://news.ycombinator.com/item?id=32116877):

- XML-RPC is “miserable design, even compared to contemporaries like Sun RPC”; “incredibly verbose”
- Only ~five primitive types; 64-bit integers need ad-hoc extensions
- Spec allows NUL in `<string>` which conflicts with standards-conforming XML parsers
- Date/time syntax is “ISO8601-ish”; timezone handling unspecified
- No XML namespaces in the base spec; extensions may or may not use them
- “The spec came from a hacked up client and server, then frozen, with all warts intact”
- Contrast with SOAP (“XML-RPC++”), JSON-RPC (“specs so simple it’s incredibly easy to implement”)
- Also: “At the time it was a revelation that you could build standard-based APIs that anyone could use with a simple library”

These are 2022 HN comment opinions, not measured facts.

### Claims made by the XML-RPC specification

From https://xmlrpc.com/spec.md (Dave Winer, 1999, updated 2003):

- `<methodName>` may contain A-Z, a-z, 0-9, underscore, dot, colon, slash; interpretation is entirely server-defined
- Scalar types: `<int>`/`<i4>` (32-bit signed), `<boolean>` (0/1, distinct from int), `<string>`, `<double>`, `<dateTime.iso8601>`, `<base64>`
- “Any characters are allowed in a string except `<` and `&`” – includes binary/NUL per spec Q&A
- `<fault>` is a struct with exactly two members: `<faultCode>` (int) and `<faultString>` (string); “A `<fault>` struct may not contain members other than those specified. This is true for all other structures.”
- There is no global list of fault codes – server-implementer defined
- Integer: 32-bit signed; plus/minus allowed; leading zeros collapsed; whitespace not permitted
- Double: decimal point notation only; no representation for infinity/NaN; range implementation-dependent
- dateTime.iso8601: “Don’t assume a timezone. It should be specified by the server in its documentation”
- Response is always HTTP 200 OK unless there’s a lower-level error; `<methodResponse>` contains either `<params>` or `<fault>`, never both

### Wikipedia tool summary

The Wikipedia tool (en.wikipedia.org/wiki/XML-RPC, accessed 2026-07-30) describes XML-RPC as an RPC protocol using XML over HTTP, created 1998 by Dave Winer / UserLand / Microsoft, evolving into SOAP. Lists standard datatypes (array, base64, boolean, dateTime, double, int/i4, string, struct) plus common extensions: nil (`<nil/>`), long/i8 (8-byte int). Includes example request/response/fault documents matching the spec format.

This is an encyclopedia summary, not authoritative for Python codec behavior.

### Current official Python documentation

From https://docs.python.org/3/library/xmlrpc.client.html (Python 3.14):

- `xmlrpc.client.ServerProxy(..., allow_none=False, use_builtin_types=False, ...)`
- If `allow_none` is true, `None` is translated to XML; default behavior is `TypeError` (“commonly used extension … isn’t supported by all clients and servers”)
- `use_builtin_types`: date/time → `datetime.datetime`, binary → `bytes`; default false
- Conformable types: boolean→`bool`, int/i1/i2/i4/i8/biginteger → `int` in range -2147483648 to 2147483647, double/float → `float`, string → `str`, array → `list`, struct → `dict` (keys must be strings), dateTime.iso8601 → `DateTime` or `datetime.datetime`, base64 → `Binary`/`bytes`/`bytearray`, nil → `None` (only if `allow_none` is true)
- Marshaller raises `TypeError` for `None` when `allow_none=False`; raises `OverflowError` for integers outside 32-bit signed range
- `xmlrpc.client.Fault` encapsulates `faultCode` (int) and `faultString` (string)
- “The xmlrpc.client module is not secure against maliciously constructed data”

### Local lab observations

See `RESULTS.md` for the full per-case table. Summary:

- Dotted RPC names (`rank.score_batch`) are opaque strings to the XML-RPC codec; the registry maps the full string to one Python callable; unknown names produce fault code 1
- `inspect.signature(fn).bind(*params)` detects arity mismatches (missing/extra) and produces fault code 2; it does **not** check annotated value types – binding `("not-a-list",)` to `score_batch(items: list)` succeeds, explicit validation then produces fault code 3
- `None` with `allow_none=False` raises `TypeError` at encode time (before dispatch); with `allow_none=True` it round-trips correctly
- Integer `2147483647` encodes successfully; `2147483648` raises `OverflowError` at encode time (marshaller enforces 32-bit signed)
- Binary data with `use_builtin_types=True` decodes to Python `bytes` (not `xmlrpc.client.Binary`)
- Boolean scores are rejected explicitly (`isinstance(score, bool)` check, since `bool` is a subclass of `int` in Python)
- Non-finite scores (`nan`, `inf`) pass through the XML-RPC double codec but are rejected by application validation
- Malformed XML raises a parser exception (`ExpatError` / `ResponseError`) – observably distinct from an XML-RPC `<fault>`
- All success and fault responses round-trip through the codec with exact value/fault code preservation

The lab does **not** prove XML-RPC is good, bad, secure, production-ready, or appropriate for a real ML service.

## Running

```bash
python run_lab.py
python -m unittest -v test_dispatch.py
```

## License

MIT
