"""Hash every candidate string with every 1990s hash and compare against the K-163 half-point x in several readings."""
import hashlib, sys
from hashes import md4, sha0, ripemd128
from strings import all_strings

TARGET = bytes.fromhex("3a5da90060df8af5be2121e601ae11f1")
T_INT = int.from_bytes(TARGET, "big")
# readings of the target: as-is; byte-reversed; 32-bit-word-swapped (little-endian words); as the low 128 of a 160-bit digest; high 128
def readings(d: bytes):
    out = {"d": d}
    if len(d) >= 16:
        out["d[:16]"] = d[:16]; out["d[-16:]"] = d[-16:]
    out["rev"] = d[::-1]
    if len(d) % 4 == 0:
        out["wswap"] = b"".join(d[i:i+4][::-1] for i in range(0, len(d), 4))
    return out
HASHES = {
    "md5": lambda b: hashlib.md5(b).digest(), "md4": md4, "sha1": lambda b: hashlib.sha1(b).digest(), "sha0": sha0,
    "ripemd128": ripemd128, "ripemd160": lambda b: hashlib.new("ripemd160", b).digest(),
    "md5(md5)": lambda b: hashlib.md5(hashlib.md5(b).digest()).digest(), "md5(hex md5)": lambda b: hashlib.md5(hashlib.md5(b).hexdigest().encode()).digest(),
    "sha1(sha1)": lambda b: hashlib.sha1(hashlib.sha1(b).digest()).digest(),
}
def match(d):
    for name, r in readings(d).items():
        if r == TARGET: return name
        # also: target with top two bits cleared is 126 bits; the hash may have had its top byte masked, or be the target XOR something trivial
        if len(r) == 16 and (int.from_bytes(r, "big") & ((1 << 126) - 1)) == T_INT: return name + " (top 2 bits masked)"
        if len(r) >= 16 and r[:15] == TARGET[:15]: return name + " (first 15 bytes!)"
    return None
n = 0; hits = []
for label, b in all_strings():
    for hname, hf in HASHES.items():
        d = hf(b); m = match(d)
        if m: hits.append((label, hname, m, d.hex())); print("HIT", label, hname, m, d.hex(), flush=True)
        n += 1
        # also hash with a counter appended (X9.62-style) 0..3
        for c in range(4):
            for cb in (bytes([c]), str(c).encode(), c.to_bytes(4, "big")):
                d2 = hf(b + cb); m = match(d2)
                if m: hits.append((label + f"+ctr{c}", hname, m, d2.hex())); print("HIT", label, hname, c, m, flush=True)
                n += 1
print(f"done: {n} hash evaluations, {len(hits)} hits")
