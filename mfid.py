"""
# MFID: a Mighty Fine Identifier

MFID gives a standards compliant timestamp-based compact
universally unique identifier.
MFID is a UUIDv7 + Crockford's Base32 representation.

**An example MFID: `0swqzb3a1sthv000xd8kta0vrw`**

Author: Edward S. Barnard <esbarnard@lbl.gov>
License: BSD
URL: https://github.com/MolecularFoundry/mfid
"""


import uuid
import base64 # part of standard library

b32_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
cb32_alphabet = "0123456789abcdefghjkmnpqrstvwxyz"

b32_to_cb32_map = dict(zip(b32_alphabet,cb32_alphabet))

def b32_to_cb32(x):
    """
    Map a base32 encoded string (without padding) 
    to a Crockford's Base32 encoded string
    
    https://www.crockford.com/base32.html
    """
    return "".join(
        [ b32_to_cb32_map[k] for k in x ]
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


def cb32_uuid4(*args, **kwargs):
    """
    Creates a 26 character encoded string based on lowercase
    Crockford's Base32 (cb32) encoding of the uuid.bytes (UUIDv7) 

    Useful as a compact random, globally unique
    identifier that can be used as a filename on most operating systems
    
    returns cb32 string and UUIDv4 object
    """
    u = uuid.uuid4(*args, **kwargs)
    cb32 = uuid_to_cb32(u)
    return cb32,u

def cb32_uuid7(*args, **kwargs):
    """
    Creates a 26 character encoded string based on lowercase
    Crockford's Base32 (cb32) encoding of the uuid.bytes (UUIDv7) 

    Useful as a compact time-based lexicographically-sortable
    identifier that can be used as a filename on most operating systems

    args and kwargs are passed to uuid7()
    
    returns cb32 string and UUIDv7 object
    """
    from uuid_extensions import uuid7 # pip install uuid7

    u = uuid7(*args, **kwargs)
    cb32 = uuid_to_cb32(u)
    return cb32,u

def mfid(*args, **kwargs):
    """
    Creates an MFID (a mighty fine identifier).
    This is a 26 character encoded string based on lowercase
    Crockford's Base32 encoding of a UUID. 
    Uses a time sequential UUIDv7 if available,
    otherwise create a random UUIDv4
    
    returns mfid string and associated UUID object as a tuple.

    example:
    >>> mfid.mfid()
    ('0sx3p4n631xck000vvs2ecrarc', UUID('067a3b12-a618-7ac9-8000-def227330ac3'))
    """    
    try:
        return cb32_uuid7(*args, **kwargs)
    except:
        return cb32_uuid4(*args, **kwargs)
    
cb32_uuid = mfid

if __name__ == '__main__':
    print(mfid())