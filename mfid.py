"""
# MFID: a Mighty Fine Identifier

MFID gives a standards compliant timestamp-based compact
universally unique identifier.
MFID is a UUIDv7 + Crockford's Base32 representation.

**An example MFID: `06g8sx7es1sdv3kffzzjm4v730`**

Author: Edward S. Barnard <esbarnard@lbl.gov>
License: BSD
URL: https://github.com/MolecularFoundry/mfid
"""


import base64
import secrets
import threading
import time
import uuid

b32_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
cb32_alphabet = "0123456789abcdefghjkmnpqrstvwxyz"

b32_to_cb32_map = dict(zip(b32_alphabet, cb32_alphabet))


def b32_to_cb32(x):
    """
    Map a base32 encoded string (without padding)
    to a Crockford's Base32 encoded string

    https://www.crockford.com/base32.html
    """
    return "".join(
        [b32_to_cb32_map[k] for k in x]
    )


def uuid_to_cb32(u):
    """Creates a 26 character encoded string based on lowercase
    Crockford's Base32 encoding of the uuid.bytes

    u: uuid object
    returns string of Crockford's Base32
    """
    # note we use typical base32 RFC 4648 alphabet in the base64
    # standard library and then convert to Crockford's by alphabet mapping
    b32 = base64.b32encode(u.bytes).decode().strip("=")
    cb32 = b32_to_cb32(b32)
    return cb32


_lock = threading.Lock()
_last_ns = 0

# One frac12 quantum is 1_000_000 / 4096 ≈ 244.14 ns. We advance by 245 ns
# to guarantee at least one frac12 increment per call even when the wall
# clock hasn't ticked (e.g. tight bursts, or coarse-resolution platforms
# like Windows without a high-precision timer).
_MIN_ADVANCE_NS = 1_000_000 // 4096 + 1  # 245


def _assemble(ns):
    ms = ns // 1_000_000
    frac12 = ((ns % 1_000_000) * 4096) // 1_000_000
    rand_b = secrets.randbits(62)
    return (
        ((ms & ((1 << 48) - 1)) << 80)
        | (0x7 << 76)
        | ((frac12 & 0xFFF) << 64)
        | (0b10 << 62)
        | rand_b
    )


def uuid7(ns=None):
    """RFC 9562 UUIDv7 using Method 3 (sub-ms fraction in rand_a).

    128-bit layout:
        bits  0-47  unix_ts_ms   millisecond Unix timestamp
        bits 48-51  version      0111
        bits 52-63  rand_a       12-bit sub-ms fraction (~244 ns resolution)
        bits 64-65  variant      10
        bits 66-127 rand_b       62 random bits

    With ns=None, uses time.time_ns() and ensures each call advances the
    logical timestamp by at least one sub-ms quantum. This guarantees
    strict monotonicity and keeps the rand_a field churning even when
    the underlying clock has coarse resolution or the call rate outpaces
    the clock. Under sustained bursts faster than ~4M IDs/sec the ID's
    embedded timestamp can lead the wall clock; timestamp_ns() returns
    the logical timestamp, not a wall-clock reading.

    With an explicit ns, returns a UUID for that timestamp with no
    monotonicity guard; useful for deterministic tests and demos.
    """
    global _last_ns
    if ns is not None:
        return uuid.UUID(int=_assemble(ns))
    with _lock:
        ns = time.time_ns()
        floor = _last_ns + _MIN_ADVANCE_NS
        if ns < floor:
            ns = floor
        _last_ns = ns
        return uuid.UUID(int=_assemble(ns))


def timestamp_ns(u):
    """Recover the generation time (nanoseconds since Unix epoch) from
    a UUIDv7 produced by this module. Resolution is ~244 ns."""
    ms = u.int >> 80
    frac = (u.int >> 64) & 0xFFF
    return ms * 1_000_000 + (frac * 1_000_000) // 4096


def cb32_uuid4():
    """Creates a 26 character MFID from a random UUIDv4.

    returns cb32 string and UUIDv4 object
    """
    u = uuid.uuid4()
    return uuid_to_cb32(u), u


def cb32_uuid7(ns=None):
    """Creates a 26 character MFID from a monotonic UUIDv7.

    ns: optional explicit nanosecond timestamp (default: time.time_ns())

    returns cb32 string and UUIDv7 object
    """
    u = uuid7(ns)
    return uuid_to_cb32(u), u


def mfid(ns=None):
    """
    Creates an MFID (a mighty fine identifier).

    A 26 character encoded string based on lowercase Crockford's Base32
    encoding of a monotonic RFC 9562 UUIDv7 (Method 3, sub-ms fraction
    embedded in rand_a for ~244 ns resolution).

    ns: optional explicit nanosecond timestamp (default: time.time_ns())

    returns mfid string and associated UUID object as a tuple.

    example:
    >>> mfid.mfid()
    ('06g8sx7es1sdv3kffzzjm4v730', UUID('01a08cf4-eec8-72dd-8e6f-7fff2a136718'))
    """
    return cb32_uuid7(ns)


cb32_uuid = mfid

if __name__ == '__main__':
    print(mfid())
