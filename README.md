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

**An example MFID: `06g8t07cm9x4b7x99w245e3xmc`**


## Using existing standards

MFID is based on the UUIDv7 standard. UUID's are [RFC standardized](https://datatracker.ietf.org/doc/rfc9562/) "universal" identifiers.  UUIDs have are 128-bit numbers with a specifc form, including randomly generated sections.
128 bits enough for every grain of sand on earth to have 10<sup>20</sup> UUIDs.
Therefore, collisions are extremely unlikely, so we can create UUIDs without checking a central database.

UUIDs are cannonically represented as a hexdecimal string with `-` seperators. This ends up giving you a 36 character representation. For Example: `064dfc00-f4e6-71ae-8000-d890eded3ecd`. MFID uses the UUIDv7 unqiue indentifier, but packs it into a more space efficent manner for use in labelling data and physical objects (See Compact Representation section below).

UUIDs v7 (part of the 2024 version of the RFC standard) has an interesting and useful property: Leading 48 bits are time ordered and represent a timestamp of creation. This means that to the millisecond time-scale UUIDv7s are lexicographically by time. The rest of the UUIDv7 bits encode randomness, avoiding collision issues.

### Anatomy of a UUIDv7 (RFC 9562 §5.7, Method 3):

```
         0                   1                   2                   3
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t1      |                       unix_ts_ms                              |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t2/t3   |          unix_ts_ms           |  ver  | sub-ms frac (12 bits) |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
t4/rand |var|                       rand (30 bits)                      |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
rand    |                          rand (32 bits)                       |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

MFID uses RFC 9562's "Method 3" variant: `rand_a` (12 bits) carries a
sub-millisecond fraction scaled to that field, giving ~244 ns time
resolution while remaining a fully valid UUIDv7. Values are strictly
monotonic on a single node.


Other non-RFC standards exist and have inspired MFID. These schemes handle many of our needs, but not all:

[**ULID**](https://github.com/ulid/spec): Handles most of the needs, but is not convertable to and from a valid RFC-defined UUID. Inspired our use of Crockerfords Base32 representation.

[**NanoID**](https://github.com/ai/nanoid): A nice compact global identifier, but random and time sorted.

## Compact representation

[Crockford’s Base32](https://www.crockford.com/base32.html) encoding scheme can take the 128bit UUIDv7 and its 36 character hexdecimal representation and compactly present the same information in 26 alphanumeric characters (09,a-z).

UUIDv7: `01a08d00-eca2-7a45-9fa9-4f0442b87da3`

transforms via CB32 to:

MFID: `06g8t07cm9x4b7x99w245e3xmc`





## Shortened MFID

We can often shorten the MFID to the first 13 characters. The first ~10 characters encode the millisecond timestamp and characters 11-13 carry the sub-millisecond fraction, so a 13-character prefix retains full ~244 ns time resolution.

Example: `06g8t07cm9x4b`

The current implementation guarantees that shortened 13-character MFIDs are unique within a single generator process — each call advances the sub-millisecond fraction by at least one quantum, even under bursts that outpace the wall clock. Uniqueness across separate processes on the same node or across different nodes is not guaranteed by the short form; use the full 26-character MFID when that matters.

## Examples

### New Years Day for years!

```python
for yr in [2023,2024,2025, 2030, 2038, 2040, 2200, 4100]:
    x = datetime(yr, 1,1,0,0,0)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(yr, mfid(ns))
...
2023 ('062pn86801r015yn3amk0nxanm', UUID('01856aa0-c800-7000-97d5-1aa93057aaad'))
2024 ('066c4mfm01r01ftpy55v4t00dg', UUID('018cc251-f400-7000-bf56-f14bb268006c'))
2025 ('06a1yabw01r016ktj3p7h15z7c', UUID('01941f29-7c00-7000-9a7a-90ec7884bf3b'))
2030 ('06wdnhdm01r016ev7e55jp3myw', UUID('01b8dac5-b400-7000-99db-3b8a595874f7'))
2038 ('07st56yc01r017dmmjgkq1jd3c', UUID('01f3a29b-cc00-7000-9db4-a4a13b864d1b'))
2040 ('08153zh401r01bse7q7gj5bg40', UUID('020251fe-2400-7000-af2e-3dcf09157020'))
2200 ('0tcyk4d801r01dpy9pvwv1cd18', UUID('0699e991-a800-7000-b6de-4db7cd858d0a'))
4100 ('7mh0d5z401r013cehescrjhmz8', UUID('3d220697-e400-7000-8d8e-8bb2cc4a34fa'))
```

### Second-resolution timestamps share the first ~7 characters
```python
for seconds in range(10):
    x = datetime(2025,1,27, 10,42,seconds)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(seconds, mfid(ns))
...
0 ('06aaepmrr1r01090vpr8sz7c3r', UUID('0194a75a-98c0-7000-8120-ddb08cfcec1e'))
1 ('06aaepmwn1r017130p5xf47d5c', UUID('0194a75a-9ca8-7000-9c23-058bd790ed2b'))
2 ('06aaepn0j1r018zjtybeyd35zw', UUID('0194a75a-a090-7000-a3f2-d796ef3465ff'))
3 ('06aaepn4f1r018259ypp9pxcgc', UUID('0194a75a-a478-7000-a045-4fad64dbac83'))
4 ('06aaepn8c1r0125shgqt89d2c4', UUID('0194a75a-a860-7000-88b9-8c2fa425a261'))
5 ('06aaepnc91r014wtrm7tcwgxar', UUID('0194a75a-ac48-7000-939a-c50fa6721d56'))
6 ('06aaepng61r01671fag9dsk6fr', UUID('0194a75a-b030-7000-98e1-7aa096e6667e'))
7 ('06aaepnm31r019x69aycgj69aw', UUID('0194a75a-b418-7000-a7a6-4abcc848c957'))
8 ('06aaepnr01r01ex66e74xwxs8g', UUID('0194a75a-b800-7000-bba6-338e4ef3b944'))
9 ('06aaepnvx1r014n6jv4eqxw45g', UUID('0194a75a-bbe8-7000-92a6-96c8ebf7842c'))
```

### Microsecond representation in the first 13 characters
```python
for microseconds in range(10):
    x = datetime(2025,1,27, 10,42,23, microsecond=microseconds)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(microseconds, mfid(ns))
...
0 ('06aaepqjk1r01bhb1fc3pqzyv4', UUID('0194a75a-f298-7000-ae2b-0bd83b5ffed9'))
1 ('06aaepqjk1r09b53fp9zktgs48', UUID('0194a75a-f298-7004-aca3-7d93f9ea1922'))
2 ('06aaepqjk1r0fdkbve31z4f0qm', UUID('0194a75a-f298-7007-b66b-db861f91e0bd'))
3 ('06aaepqjk1r0s6d9s7j4yskdam', UUID('0194a75a-f298-700c-99a9-c9e44f666d55'))
4 ('06aaepqjk1r11ckmc226zx5nc0', UUID('0194a75a-f298-7010-b274-60846ff4b560'))
5 ('06aaepqjk1r19e1dvz82hjfpzm', UUID('0194a75a-f298-7014-b82d-dfd028c9f6fd'))
6 ('06aaepqjk1r1h6angjnj3dh9am', UUID('0194a75a-f298-7018-9955-84ab21b62955'))
7 ('06aaepqjk1r1s9f1a4da3s7z1m', UUID('0194a75a-f298-701c-a5e1-511aa1e4ff0d'))
8 ('06aaepqjk1r23cdccg3d1yma2w', UUID('0194a75a-f298-7021-b1ac-6406d0fa8a17'))
9 ('06aaepqjk1r29935v5q0n19340', UUID('0194a75a-f298-7024-a465-d96e0a852320'))
```

### Randomness helps with identical timestamps across the world

Example (**rand**): 06aaepqjk1wg3**4cj1cv1hacjjm**

```python
for i in range(10):
    x = datetime(2025,1,27, 10,42,23,563)
    ns = int(x.replace(tzinfo=timezone.utc).timestamp()*10**9)
    print(i, mfid(ns))
...
0 ('06aaepqjk1wg34cj1cv1hacjjm', UUID('0194a75a-f298-7901-9192-0b3618a99295'))
1 ('06aaepqjk1wg30c15wer2f05rc', UUID('0194a75a-f298-7901-8181-2f1d813c05c3'))
2 ('06aaepqjk1wg34pq8r3azvm6x4', UUID('0194a75a-f298-7901-92d7-4606afee86e9'))
3 ('06aaepqjk1wg3amf4x3nhjvb6c', UUID('0194a75a-f298-7901-aa8f-274758cb6b33'))
4 ('06aaepqjk1wg3dnyr1k3c7d6ym', UUID('0194a75a-f298-7901-b6be-c066361da6f5'))
5 ('06aaepqjk1wg399zabnqbd8db0', UUID('0194a75a-f298-7901-a53f-52eb75b50d58'))
6 ('06aaepqjk1wg373j5cvzn2z37m', UUID('0194a75a-f298-7901-9c72-2b37fa8be33d'))
7 ('06aaepqjk1wg38aeqx9h86mhag', UUID('0194a75a-f298-7901-a14e-bf53141a9154'))
8 ('06aaepqjk1wg3aseskbqzqps9g', UUID('0194a75a-f298-7901-ab2e-ccd77fded94c'))
9 ('06aaepqjk1wg3d4j6m4be6d4a0', UUID('0194a75a-f298-7901-b492-3508b719a450'))
```

### Coarse-clock or tight-burst worst case

The examples above all pass an explicit `ns` to `mfid()`, which bypasses the monotonicity guard on purpose. In real use — where `mfid()` reads the wall clock itself — a run of calls landing on the same reported `time.time_ns()` value (a coarse-resolution platform, or a burst faster than the clock ticks) still produces distinct 13-character prefixes, because the generator enforces at least one `rand_a` quantum of advance per call.

Simulating that worst case by pinning `time.time_ns()` to a single value:

```python
import time, mfid

_orig = time.time_ns
time.time_ns = lambda: 1_737_974_543_000_563_000  # frozen wall clock
try:
    for i in range(10):
        print(i, mfid.mfid())
finally:
    time.time_ns = _orig
...
0 ('06aaepqjk1wg510ae5f1pef7a4', UUID('0194a75a-f298-7902-840a-715e1b39e751'))
1 ('06aaepqjk1wg7ct1q7ma9p14v0', UUID('0194a75a-f298-7903-b341-b9e8a4d824d8'))
2 ('06aaepqjk1wg9anbze6nb3fxvr', UUID('0194a75a-f298-7904-aaab-fb8d558dfdde'))
3 ('06aaepqjk1wgbf7gm7gzq5w74c', UUID('0194a75a-f298-7905-bcf0-a1e1fb978723'))
4 ('06aaepqjk1wgd28c8crzq13s4w', UUID('0194a75a-f298-7906-890c-4331fb847927'))
5 ('06aaepqjk1wgf049n7qefqfqz8', UUID('0194a75a-f298-7907-8089-a9eee7ddf7fa'))
6 ('06aaepqjk1wgh7fm9pq0za5ybg', UUID('0194a75a-f298-7908-9df4-4dae0fa8be5c'))
7 ('06aaepqjk1wgk03whss35jatz0', UUID('0194a75a-f298-7909-807c-8e7232c95af8'))
8 ('06aaepqjk1wgnaqr11mm4eg668', UUID('0194a75a-f298-790a-aaf8-0869423a0632'))
9 ('06aaepqjk1wgqessnftex6sg3c', UUID('0194a75a-f298-790b-bb39-abf4ee9b301b'))
```

The wall clock never moved, yet the `rand_a` field (visible as the last hex group before the variant, `7902` → `7903` → `7904` …) advances by one quantum each call, and every 13-character prefix (`06aaepqjk1wg5`, `06aaepqjk1wg7`, `06aaepqjk1wg9`, …) is distinct.

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
('06g8t07cm9x4b7x99w245e3xmc', UUID('01a08d00-eca2-7a45-9fa9-4f0442b87da3'))
```

The function `mfid()` creates a 26 character encoded string based on lowercase Crockford's Base32 encoding of an RFC 9562 UUIDv7. It returns a tuple of the mfid string and the associated UUID object.

MFID ships its own self-contained UUIDv7 generator (RFC 9562 §5.7, Method 3), so it has no runtime dependencies. Values are strictly monotonic on a single node, and the 12-bit sub-millisecond fraction embedded in `rand_a` gives ~244 ns time resolution — enough that rapid successive calls remain distinguishable even after truncating the MFID.

The generation timestamp can be recovered with `mfid.timestamp_ns(uuid_obj)`.

### Clock resolution and cross-platform behavior

The Python standard library's `uuid.uuid7()` (added in 3.14) uses a 42-bit monotonic counter within each millisecond rather than a sub-ms timestamp fraction, because `time.time_ns()` does not have sub-ms precision on every platform:

| Platform | Effective `time.time_ns()` resolution |
| --- | --- |
| Linux (`clock_gettime`) | ~1 ns |
| macOS (`gettimeofday`) | ~1 μs |
| Windows 8+ (`GetSystemTimePreciseAsFileTime`) | ~1 μs |
| Windows 7 and earlier | ~15.6 ms |
| WASM / Pyodide | ~100 μs |

To keep the "sub-ms information in the first 13 characters" property working everywhere — including on coarse-clock platforms and under bursts that outpace the clock — MFID's generator enforces a minimum advance of one `rand_a` quantum (~245 ns) per call. When the wall clock hasn't moved that far, the generator synthesizes the advance itself. This guarantees:

- Strict monotonicity regardless of clock precision or backward clock steps
- Up to 4,096 unique 13-character prefixes per real millisecond
- Full 26-character uniqueness under any load

Under sustained bursts faster than ~4 million IDs per second the ID's embedded timestamp can lead the wall clock, so `timestamp_ns()` returns a *logical* timestamp — close to wall time in normal use, but not a substitute for a separately recorded wall-clock reading if that is what you actually need.

See the [MFID v1 vs v2](#mfid-v1-vs-v2) section below for the bit-layout changes between the v1 release and v2.


## Annotated example

Taking a single MFID generated for `ns = 1737936000000500000` (2025-01-27 00:00:00.000500 UTC):

```
UUID:  0194a50e-d400-77ff-8b2e-476c0d7ee186
MFID:  06aaa3pm01 | vzz | 2se8xp0tzq1gr
       └─── A ───┘  └─B─┘  └─── C ─────┘
```

**A — chars 1–10** — the 48-bit `unix_ts_ms` timestamp (2025-01-27 00:00:00.000 UTC). Chars 1–9 hold 45 of the 48 ms bits; char 10 carries the last 3 ms bits plus the top 2 bits of the version nibble.

**B — chars 11–13** — the 12-bit `rand_a` field, which MFID uses as a sub-millisecond fraction (~244 ns quantum). Char 11 also carries the low 2 bits of the version (`11`); char 13 carries the high bit of the variant (`1`, so char 13 is always odd in Crockford Base32). Two MFIDs from the same real millisecond differ only in this slice (and in C).

**C — chars 14–26** — 62 random bits (`rand_b`) with the low bit of the variant (`0`) stuck on the front and 2 zero pad bits stuck on the tail. Char 14 always has `0` as its top bit, and char 26 is always one of `0 4 8 c g m s x` (its bottom two bits are the padding zeros).

### The bits per character, exactly

Because 128 UUID bits ÷ 5 bits/char = 25.6 chars, the logical UUID fields don't line up cleanly on Base32 boundaries. Here's what every char actually contains:

| Char | Bits | Contains |
| --- | --- | --- |
| 1–9 | 0–44 | ms timestamp bits 0–44 |
| 10 | 45–49 | ms bits 45–47, version bits 0–1 (`01`) |
| 11 | 50–54 | version bits 2–3 (`11`), rand_a bits 0–2 |
| 12 | 55–59 | rand_a bits 3–7 |
| 13 | 60–64 | rand_a bits 8–11, variant bit 0 (always `1`) |
| 14 | 65–69 | variant bit 1 (always `0`), rand_b bits 0–3 |
| 15–25 | 70–124 | rand_b bits 4–58 |
| 26 | 125–129 | rand_b bits 59–61, 2 padding zeros |

The practical short-form rule of thumb — "first ~10 chars are the time, chars 11–13 are the sub-ms fraction, the rest is random" — is accurate to within a few bits at each seam, and the seams are the fixed version/variant bits that don't carry data anyway.


## MFID v1 vs v2

MFID v1 was built on the pre-RFC IETF draft for UUIDv7 (via the `uuid7` PyPI package). MFID v2 targets the ratified [RFC 9562 §5.7](https://datatracker.ietf.org/doc/html/rfc9562.html#section-5.7), Method 3, with a self-contained implementation and no external dependencies. This also aligns MFID's byte layout with Python 3.14's stdlib `uuid.uuid7()` for the shared portions.

Both v1 and v2 are valid UUIDv7 values according to their respective specifications, both are 26 Crockford Base32 characters, and both are lexicographically sortable *within* their own format. But the internal bit layouts differ, so v1 and v2 MFIDs are not directly interchangeable.

### Bit layout

| Field | v1 (draft) | v2 (RFC 9562 Method 3) |
| --- | --- | --- |
| Timestamp | 36-bit **whole seconds** since Unix epoch | 48-bit **milliseconds** since Unix epoch |
| Sub-second precision | 24-bit fractional-seconds field (~60 ns quantum) | 12-bit `rand_a` used as sub-ms fraction (~244 ns quantum) |
| Version | 4 bits, interleaved between the two halves of the sub-second field | 4 bits, contiguous, immediately after the ms timestamp |
| Monotonicity | 14-bit sequence counter | Enforced by ≥1 quantum advance per call in `mfid.uuid7()` |
| Random tail (`rand_b`) | 48 bits | 62 bits |
| Timestamp overflow | year ~4147 (36-bit seconds) | year ~10899 (48-bit ms) |

### Sort order across versions

Even at the exact same wall-clock instant, a v1 MFID and a v2 MFID look completely different, because they encode different numeric quantities into differently-sized fields. For any timestamp in the practical lifetime of v1:

**v2 sorts before v1 in lexicographic order.**

v2's 48-bit ms field has ~7 more leading zero bits than v1's 36-bit seconds field for the same instant — about 1.4 more leading Crockford Base32 zeros at the front of every v2 MFID. Example:

```
v1 at 2026-02-10:  0tn31j3mj9yf1000v9wjf18mj0
v2 at 2026-02-10:  06g8st7gesv6b7rzttpgy1vhbm
```

Char 1 is `0` for both, but char 2 diverges: `t` (26) for v1 vs `6` (6) for v2. `'6' < 't'`, so v2 sorts earlier.

This relationship holds through roughly year 4147, at which point v1's 36-bit seconds field overflows and v1 becomes unusable for further generation.

### What this means for existing data

- **Existing v1 MFIDs stay valid and unique.** They continue to parse as valid UUIDv7 objects and still sort in creation order relative to other v1 MFIDs.
- **`mfid.timestamp_ns()` must not be used on v1 IDs.** Its bit interpretation is v2-specific.
- **v1 and v2 MFIDs do not interleave correctly in a time-sorted collection.** In a mixed collection, all v2 MFIDs sort as if they were "earlier" than v1 MFIDs of the same wall-clock time. If you're combining historical v1 IDs with newly-generated v2 IDs and rely on time ordering, either regenerate the old IDs or keep the two sets in separate sort spaces.
- **Migration is transparent.** `pip install --upgrade mfid` moves you from v1 to v2, and v2 has no runtime dependencies at all — the `uuid7` package can be uninstalled.


## Author

Edward S. Barnard <esbarnard@lbl.gov>
