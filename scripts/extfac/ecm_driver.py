"""Run a bounded, recorded GMP-ECM search; no factor-size completeness is implied."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze import is_probable_prime, SMALL
from cover import curves as CANDIDATES
from extfac.cofactors import extension_components
from factorization import check_prime_factors

ECM = os.environ.get("ECM", "ecm")
LEVELS = [(50000, 280), (250000, 215)]


def trial(value):
    factors = []
    for q in SMALL:
        if q * q > value:
            break
        while value % q == 0:
            factors.append(q)
            value //= q
    return factors, value


def write_transcript(path, command, value, code, stdout, stderr):
    if path is None:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stdout = stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout or ""
    stderr = stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr or ""
    path.write_text(f"command: {json.dumps(command)}\ninput: {value}\nexit: {code}\n"
                    f"\nSTDOUT\n{stdout}\nSTDERR\n{stderr}", encoding="utf-8")


def ecm_once(value, bound, curves, transcript_path=None):
    if value < 2 or bound < 2 or curves < 1:
        raise ValueError("Invalid ECM input, bound, or curve count")
    command = [ECM, "-one", "-c", str(curves), str(bound)]
    try:
        result = subprocess.run(command, input=str(value) + "\n", capture_output=True,
                                text=True, timeout=3600)
    except subprocess.TimeoutExpired as error:
        write_transcript(transcript_path, command, value, "timeout", error.stdout, error.stderr)
        raise RuntimeError("GMP-ECM timed out; no completed search budget is inferred") from error
    write_transcript(transcript_path, command, value, result.returncode, result.stdout, result.stderr)
    if result.returncode not in (0, 2, 6, 8, 10, 14) or result.stderr.strip():
        raise RuntimeError(f"GMP-ECM failed (exit {result.returncode}):\n{result.stderr}\n{result.stdout}")
    found = re.findall(r"Found (?:probable )?(?:prime|composite) factor of \d+ digits: (\d+)",
                       result.stdout)
    if len(found) > 1:
        raise RuntimeError("GMP-ECM returned multiple factors despite -one; transcript was not consumed")
    factor = int(found[0]) if found else None
    if bool(factor) != (result.returncode in (2, 6, 10, 14)):
        raise RuntimeError("GMP-ECM factor output and exit status disagree")
    if factor is not None and (not 1 < factor < value or value % factor):
        raise RuntimeError(f"GMP-ECM returned a non-proper factor of {value}: {factor}")
    runs = [(int(i), int(total)) for i, total in re.findall(r"Run (\d+) out of (\d+)", result.stdout)]
    # GMP-ECM 7 omits the first "Run" heading, even with -c greater than one.
    started = len(re.findall(r"^Using B1=", result.stdout, re.M))
    if started:
        used = started
        if not 1 <= used <= curves:
            raise RuntimeError("GMP-ECM started more curves than requested")
        if runs and (any(total != curves for _, total in runs)
                     or runs[0][0] not in (1, 2)
                     or [i for i, _ in runs] != list(range(runs[0][0], used + 1))):
            raise RuntimeError("Invalid or incomplete GMP-ECM run counters")
        if result.returncode == 0 and len(re.findall(r"^Step 1 took\b", result.stdout, re.M)) != used:
            raise RuntimeError("GMP-ECM output has no completion record for each curve")
    elif result.returncode == 8 and runs:
        if any(total != curves for _, total in runs) or not 1 <= runs[-1][0] <= curves:
            raise RuntimeError("Invalid GMP-ECM degenerate-curve counter")
        used = runs[-1][0]
    else:
        raise RuntimeError("GMP-ECM did not report the completed curve count")
    if factor is None and result.returncode == 0 and used != curves:
        raise RuntimeError("GMP-ECM terminated before completing the requested no-factor search")
    return factor, used


def factor(value, log_dir=None):
    if value < 2:
        raise ValueError("Factorization input must exceed one")
    original = value
    factors, pending = [], []

    def enqueue(part):
        small, rest = trial(part)
        factors.extend(small)
        if rest > 1:
            if is_probable_prime(rest):
                factors.append(rest)
            else:
                pending.append(rest)

    enqueue(value)
    log, attempt = [], 0
    for bound, budget in LEVELS:
        left = budget
        while pending and left:
            target = pending.pop()
            attempt += 1
            path = Path(log_dir) / f"attempt-{attempt:04d}.txt" if log_dir is not None else None
            found, used = ecm_once(target, bound, left, path)
            if not 1 <= used <= left:
                raise RuntimeError("ECM curve accounting exceeded the remaining budget")
            left -= used
            if found is None:
                pending.append(target)
                continue
            if not 1 < found < target or target % found:
                raise RuntimeError("ECM returned an invalid divisor")
            enqueue(found)
            enqueue(target // found)
        log.append([bound, budget - left])
    cofactor = math.prod(pending)
    check_prime_factors(original, factors, cofactor)
    return sorted(factors), cofactor, log


def read_inputs(path):
    candidates = {(c["run"], c["i"]): c for c in CANDIDATES}
    rows, seen = [], set()
    with Path(path).open() as source:
        for lineno, line in enumerate(source, 1):
            fields = line.split()
            if len(fields) != 5:
                raise ValueError(f"{path}:{lineno}: expected run, index, label, degree, value")
            run, index, label, degree, value = fields
            index, degree, value = int(index), int(degree), int(value)
            key = run, index, degree
            if key in seen:
                raise ValueError(f"Duplicate ECM input: {key}")
            seen.add(key)
            c = candidates.get((run, index))
            if c is None or degree not in (3, 4, 6) or label not in ("pub", "skip"):
                raise ValueError(f"Unknown ECM input: {key}")
            if (label == "pub") != c["pub"] or value != extension_components(c["p"], c["t"])[degree]:
                raise ValueError(f"ECM input does not match the curve: {key}")
            rows.append((run, index, label, degree, value))
    expected = {(c["run"], c["i"], k) for c in CANDIDATES for k in (3, 4, 6)}
    if seen != expected:
        raise ValueError("ECM input must contain all 57 unique curve/degree combinations before sharding")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("shard", nargs="?", type=int, default=0)
    parser.add_argument("mod", nargs="?", type=int, default=1)
    args = parser.parse_args()
    if args.mod < 1 or not 0 <= args.shard < args.mod:
        raise ValueError("Require 0 <= shard < mod")
    inputs = read_inputs(args.input)
    logs = args.output.with_suffix(".logs")
    checkpoint = args.output.with_name(args.output.name + ".next")
    if args.output.exists() or logs.exists() or checkpoint.exists():
        raise FileExistsError("Choose a new output path; existing results/transcripts will not be overwritten")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    logs.mkdir()
    with args.output.open("x", encoding="utf-8") as f:
        f.write("[]\n")
    rows = []
    for j, (run, index, label, degree, value) in enumerate(inputs):
        if j % args.mod != args.shard:
            continue
        start = time.monotonic()
        row_logs = logs / f"{run}-{index}-k{degree}"
        row_logs.mkdir()
        factors, cofactor, completed = factor(value, row_logs)
        rows.append(dict(run=run, i=index, pub=label == "pub", k=degree,
                         bits=value.bit_length(), factors=[str(f) for f in factors],
                         factor_bits=[f.bit_length() for f in factors],
                         cofactor=str(cofactor),
                         cofactor_bits=cofactor.bit_length() if cofactor > 1 else 0,
                         cofactor_prime=is_probable_prime(cofactor) if cofactor > 1 else None,
                         log=completed, secs=round(time.monotonic() - start),
                         coverage={"status": "bounded-recorded", "trial_bound": 10**6,
                                   "levels_requested": LEVELS, "levels_completed": completed,
                                   "exhaustive": False, "protocol": "-one",
                                   "raw_transcripts": str(row_logs.relative_to(args.output.parent))}))
        with checkpoint.open("x", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)
            f.write("\n")
        checkpoint.replace(args.output)
        print(f"{run} {index} k={degree}: {len(factors)} known prime factors, "
              f"remaining {cofactor.bit_length() if cofactor > 1 else 0} bits", flush=True)
    if not rows:
        print(f"Shard {args.shard}/{args.mod}: no assigned inputs; wrote an empty result list")


if __name__ == "__main__":
    main()
