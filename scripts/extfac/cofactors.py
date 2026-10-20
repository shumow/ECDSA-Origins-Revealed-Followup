"""Write extension-order components for the nineteen viable candidates."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze2 import DATA_DIR
from cover import curves


def ords(p, t, limit):
    traces = {0: 2, 1: t}
    for k in range(2, limit + 1):
        traces[k] = t * traces[k - 1] - p * traces[k - 2]
    return {k: p**k + 1 - traces[k] for k in range(1, limit + 1)}


def extension_components(p, t):
    return {3: p*p + (t - 1)*p + t*t + t + 1,
            4: (p - 1)**2 + t*t,
            6: p*p - (t + 1)*p + t*t - t + 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path,
                        default=DATA_DIR.parent / "results" / "ecm-work" / "cof.txt")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for c in curves:
            p, n, t = c["p"], c["n"], c["t"]
            orders = ords(p, t, 6)
            components = extension_components(p, t)
            if (components[3] * n != orders[3] or components[4] * orders[2] != orders[4]
                    or components[6] * orders[3] * orders[2] != orders[6] * n):
                raise ValueError(f"Extension-order identity failed for {c['run']}/{c['i']}")
            for k, value in components.items():
                f.write(f"{c['run']} {c['i']} {'pub' if c['pub'] else 'skip'} {k} {value}\n")
    print(f"Wrote extension components to {args.output}")


if __name__ == "__main__":
    main()
