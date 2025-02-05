# MFID: a Mighty Fine Identifier

A compact universal persistent identifier is useful in many contexts, 
especially in scientific and engineering disiplines that happen distributed around the world. 
 
We would like to uniquely identify data sets, samples, without coordinating the generation of such identifiers.

Guiding principles for creating an identifier scheme:

 - Global uniqueness 
 - Compact
 - Human readable/typeable
 - Lexicographically sortable (by time)
 - Used as a filename (limits on filesystems: case-sensitivity, length, allowable characters)
 - Use existing standards as much as possible

**Short TL;DR:** MFID is a UUIDv7 + Crockford's Base32 representation. MFID gives a standards compliant timestamp-based compact universally unique identifier.

**An example MFID: `0swqzb3a1sthv000xd8kta0vrw`**


## Using existing standards

MFID is based on the UUIDv7 standard. UUID's are [RFC standardized](https://datatracker.ietf.org/doc/rfc9562/) "universal" identifiers.  UUIDs have are 128-bit numbers with a specifc form, including randomly generated sections.
128 bits enough for every grain of sand on earth to have 10<sup>20</sup> UUIDs.
Therefore, collisions are extremely unlikely, so we can create UUIDs without checking a central database.

UUIDs are cannonically represented as a hexdecimal string with `-` seperators. This ends up giving you a 36 character representation. For Example: `064dfc00-f4e6-71ae-8000-d890eded3ecd`. MFID uses the UUIDv7 unqiue indentifier, but packs it into a more space efficent manner for use in labelling data and physical objects (See Compact Representation section below).

UUIDs v7 (part of the 2024 version of the RFC standard) has an interesting and useful property: Leading XX bits are time ordered and represent a timestamp of creation. This means that to the millisecond time-scale UUIDv7s are lexicographically by time. The rest of the UUIDv7 bits encode randomness, avoiding collision issues.

### Anatomy of a UUIDv7 (borrowed from python package `uuidv7`):

```
         0                   1                   2                   3
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t1      |                 unixts (secs since epoch)                     |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t2/t3   |unixts |  frac secs (12 bits)  |  ver  |  frac secs (12 bits)  |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t4/rand |var|       seq (14 bits)       |          rand (16 bits)       |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
rand    |                          rand (32 bits)                       |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```


Other non-RFC standards exist and have inspired MFID. These schemes handle many of our needs, but not all:

[**ULID**](https://github.com/ulid/spec): Handles most of the needs, but is not convertable to and from a valid RFC-defined UUID. Inspired our use of Crockerfords Base32 representation.

[**NanoID**](https://github.com/ai/nanoid): A nice compact global identifier, but random and time sorted.

## Compact representation

[Crockford’s Base32](https://www.crockford.com/base32.html) encoding scheme can take the 128bit UUIDv7 and its 36 character hexdecimal representation and compactly present the same information in 26 alphanumeric characters (09,a-z).

UUIDv7: `06797fac-6a0e-751d-8000-eb513d281bc7` 

transforms via CB32 to:

MFID: `0swqzb3a1sthv000xd8kta0vrw`





## Shortened MFID

For cases when microsecond time-based collisions are unlikely, we can often shorten the MFID to the first 13 characters, skipping the version ID and random portions of the UUIDv7:

Example: `0swqzb3a1sthv`

## Examples

### New Years Day for years!

```python
for yr in [2023,2024,2025, 2030, 2038, 2040, 2200, 4100]:
    x = datetime(yr, 1,1,0,0,0)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(yr, mfid(ns))
...
2023 ('0rxgsm0001r010006jjjm8t8ng', UUID('063b0cd0-0000-7000-8000-34a52a2348ac'))
2024 ('0scj020001r01000w7rcx2j4hw', UUID('06592008-0000-7000-8000-e1f0ce8a448f'))
2025 ('0svmgp0001r010007b7cwx3jz8', UUID('06774858-0000-7000-8000-3acece7472fa'))
2030 ('0w6vv20001r01000dhzrn9hpyw', UUID('070dbd88-0000-7000-8000-6c7f8aa636f7'))
2038 ('0zz82y0001r010006ekbn2c3w8', UUID('07fe8178-0000-7000-8000-33a6ba8983e2'))
2040 ('10xaft0001r01000qwbh0mmxvm', UUID('083aa7e8-0000-7000-8000-bf1710529ddd'))
2200 ('3c4y340001r010000ha7kk1pj4', UUID('1b09e190-0000-7000-8000-045479cc3691'))
4100 ('z9k82t0001r0100006969dz8ec', UUID('fa668168-0000-7000-8000-019264b7e873'))
```

### Second timestamps in the first 8 characters
```python
for seconds in range(10):
    x = datetime(2025,1,27, 10,42,seconds)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(seconds, mfid(ns))
...
0 ('0swqcbw001s3q000gsrdyz9378', UUID('0679762f-8000-723b-8000-8670df7d233a'))
1 ('0swqcbwg01s3q000bqmjy1mtw8', UUID('0679762f-9000-723b-8000-5de92f069ae2'))
2 ('0swqcbx001s3q0001hhksjsvy4', UUID('0679762f-a000-723b-8000-0c633ccb3bf1'))
3 ('0swqcbxg01s3q000sbvrwte3nm', UUID('0679762f-b000-723b-8000-caf78e69c3ad'))
4 ('0swqcby001s3q0009egs4xa0bg', UUID('0679762f-c000-723b-8000-4ba19275405c'))
5 ('0swqcbyg01s3q00015edb5wwnm', UUID('0679762f-d000-723b-8000-095cd5979cad'))
6 ('0swqcbz001s3q000acpnac54s0', UUID('0679762f-e000-723b-8000-532d5530a4c8'))
7 ('0swqcbzg01s3q000wvqaa411sw', UUID('0679762f-f000-723b-8000-e6eea51021cf'))
8 ('0swqcc0001s3q000vp989v3gfg', UUID('06797630-0000-723b-8000-dd9284ec707c'))
9 ('0swqcc0g01s3q000p7x2a1ez28', UUID('06797630-1000-723b-8000-b1fa2505df12'))
```

### Microsecond representation in the first 13 characters
```python
for microseconds in range(10):
    x = datetime(2025,1,27, 10,42,23, microsecond=microseconds)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(microseconds, mfid(ns))
...
0 ('0swqcc7g01r01000307p2d6p5r', UUID('06797630-f000-7000-8000-180f6134d62e'))
1 ('0swqcc7g01r1300068qb5q6a0m', UUID('06797630-f000-7011-8000-322eb2dcca05'))
2 ('0swqcc7g01r1x000qkqafxsw2r', UUID('06797630-f000-701e-8000-bceea7f73c16'))
3 ('0swqcc7g01r37000sbxpjk39er', UUID('06797630-f000-7033-8000-cafb694c6976'))
4 ('0swqcc7g01r49000ezrr6jbtt4', UUID('06797630-f000-7044-8000-77f183497ad1'))
5 ('0swqcc7g01r5b0009rec26p9g8', UUID('06797630-f000-7055-8000-4e1cc11ac982'))
6 ('0swqcc7g01r650004bs8egfwrr', UUID('06797630-f000-7062-8000-22f28741fcc6'))
7 ('0swqcc7g01r770006k9jrrgp2m', UUID('06797630-f000-7073-8000-34d32c621615'))
8 ('0swqcc7g01r8k000vvctva7eem', UUID('06797630-f000-7089-8000-ded9ada8ee75'))
9 ('0swqcc7g01r9d000j21jksndv0', UUID('06797630-f000-7096-8000-908329e6add8'))
```

### Randomness helps with identical timestamps
```python
for i in range(10):
    x = datetime(2025,1,27, 10,42,23,563)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(i, mfid(ns))
...
0 ('0swqcc7g09te9000qzbx6hybcc', UUID('06797630-f002-74e4-8000-bfd7d347cb63'))
1 ('0swqcc7g09te9001n0pp3repmg', UUID('06797630-f002-74e4-8001-a82d61e1d6a4'))
2 ('0swqcc7g09te90021zgr40n04g', UUID('06797630-f002-74e4-8002-0fe18202a024'))
3 ('0swqcc7g09te9003a04nkksdgg', UUID('06797630-f002-74e4-8003-500959cf2d84'))
4 ('0swqcc7g09te9004ab86st4jz8', UUID('06797630-f002-74e4-8004-52d06ce892fa'))
5 ('0swqcc7g09te9005p5mqczg7ac', UUID('06797630-f002-74e4-8005-b169767e0753'))
6 ('0swqcc7g09te9006ncvx7ht68c', UUID('06797630-f002-74e4-8006-ab37d3c74643'))
7 ('0swqcc7g09te9007kkw28mqk9r', UUID('06797630-f002-74e4-8007-9cf82452f34e'))
8 ('0swqcc7g09te9008xhrrs70qh0', UUID('06797630-f002-74e4-8008-ec718c9c1788'))
9 ('0swqcc7g09te90090knvrvb0gc', UUID('06797630-f002-74e4-8009-04ebbc6d6083'))
```

## Python implementation


```console
$ pip install mfid
```

```python
from mfid import mfid
mfid_str, uuid_obj = mfid()
```

```pycon     
>>> import mfid  
>>> mfid.mfid()
('0sx3p4n631xck000vvs2ecrarc', UUID('067a3b12-a618-7ac9-8000-def227330ac3'))
```

The function `mfid()`creates a 26 character encoded string based on lowercase Crockford's Base32 encoding of a UUID. 
Uses a time sequential UUIDv7 if available, otherwise create a random UUIDv4. It returns a tuple of mfid string and the associated UUID object.

Note that the python standard library does not include a UUIDv7 generator yet, so we rely on the [`uuidv7`](https://pypi.org/project/uuid7/) package for UUID generation. MFID will fallback to UUIDv4 (fully random) if UUIDv7 is unavailable.


## Author

Edward S. Barnard <esbarnard@lbl.gov>
