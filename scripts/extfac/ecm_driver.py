"""Run bounded GMP-ECM on each extension-order cofactor, stripping factors as they are found.
usage: ecm_driver.py cof.txt out.json [shard mod]"""
import json, re, subprocess, sys, time
sys.path.insert(0, "..")
from analyze import is_probable_prime, SMALL

ECM = "ecm"
LEVELS = [(50000, 280), (250000, 215)]  # (B1, curves): full t25, half of t30

def trial(N):
    fs = []
    for q in SMALL:
        if q * q > N: break
        while N % q == 0: fs.append(q); N //= q
    return fs, N

def ecm_once(N, B1, curves):
    r = subprocess.run([ECM, "-c", str(curves), str(B1)], input=str(N) + "\n", capture_output=True, text=True)
    m = re.search(r"Found (?:probable )?(?:prime|composite) factor of \d+ digits: (\d+)", r.stdout)
    runs = re.findall(r"Run (\d+) out of", r.stdout)
    used = int(runs[-1]) if (runs and m) else curves
    return (int(m.group(1)) if m else None), used

def factor(N):
    fs, N = trial(N)
    log = []
    for B1, curves in LEVELS:
        left = curves
        while left > 0 and N > 1 and not is_probable_prime(N):
            f, used = ecm_once(N, B1, left)
            left -= used
            if f is None: break
            if not is_probable_prime(f):
                sub, rest = trial(f); fs += sub; f = rest
                if f > 1 and not is_probable_prime(f): log.append(("composite factor", f)); fs.append(f); N //= f; continue
            if f > 1: fs.append(f); N //= f
        log.append((B1, curves - left))
    return sorted(fs), N, log

rows = []
shard, mod = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)
for j, line in enumerate(open(sys.argv[1])):
    if j % mod != shard: continue
    run, idx, lab, k, C = line.split(); C = int(C); k = int(k)
    t0 = time.time()
    fs, cof, log = factor(C)
    rows.append(dict(run=run, i=int(idx), pub=lab == "pub", k=k, bits=C.bit_length(), factors=[str(f) for f in fs],
                     factor_bits=[f.bit_length() for f in fs], cofactor_bits=cof.bit_length() if cof > 1 else 0,
                     cofactor_prime=is_probable_prime(cof) if cof > 1 else None, cofactor=str(cof), log=log, secs=round(time.time() - t0)))
    print(run, idx, lab, "k=%d" % k, "factor bits", [f.bit_length() for f in fs], "cof", cof.bit_length(), "P" if cof > 1 and is_probable_prime(cof) else "C", "%.0fs" % (time.time() - t0), flush=True)
    json.dump(rows, open(sys.argv[2], "w"), indent=1)
