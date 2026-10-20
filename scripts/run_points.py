"""Regenerate selected point results in a fresh directory, preserving other curves."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def merge_blocks(old, new, header):
    def blocks(text):
        found = list(re.finditer(header, text, re.M))
        if text.strip() and (not found or found[0].start() != 0):
            raise ValueError("Unrecognized point-result header")
        result = {}
        for j, match in enumerate(found):
            end = found[j + 1].start() if j + 1 < len(found) else len(text)
            key = match.group(0)
            if key in result:
                raise ValueError(f"Duplicate point-result block: {key}")
            result[key] = text[match.start():end]
        return result
    original, updates = blocks(old), blocks(new)
    if not updates:
        raise ValueError("No regenerated point-result blocks")
    if set(updates) - set(original):
        raise ValueError("Regenerated point results contain unexpected curve keys")
    original.update(updates)
    return "".join(original.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--curve", choices=("P-224", "P-521"), default="P-224")
    selection.add_argument("--all", action="store_true", help="Repeat all point scans")
    args = parser.parse_args()
    path = str(ROOT / "scripts" / "pts.gp").replace("\\", "\\\\").replace('"', '\\"')
    selected = "" if args.all else args.curve
    script = f'ONLY="{selected}";read("{path}");quit\n'
    with tempfile.TemporaryDirectory(prefix="nist-points-") as directory:
        result = subprocess.run([os.environ.get("GP", "gp"), "-fq", "-s", "1000000000"],
                                input=script, capture_output=True, text=True, cwd=directory, timeout=3600)
        if result.returncode or result.stderr.strip() or "POINT_SCAN_OK" not in result.stdout:
            raise RuntimeError(f"PARI point scan failed (exit {result.returncode}, "
                               f"completed={'POINT_SCAN_OK' in result.stdout}):\n"
                               f"{result.stderr}\n{result.stdout}")
        outputs = {}
        expected = {"mult.out"} if selected == "P-521" else {"pts.out", "mult.out"}
        for name, header in (("pts.out", r"^\S+ \d+ small-x points"),
                             ("mult.out", r"^\S+: G on curve")):
            produced = Path(directory) / name
            if name not in expected:
                if produced.exists():
                    raise RuntimeError(f"Unexpected point output: {name}")
                continue
            target = ROOT / "results" / name
            outputs[target] = merge_blocks(target.read_text(encoding="utf-8"),
                                           produced.read_text(encoding="utf-8"), header)
        for target, text in outputs.items():
            target.write_text(text, encoding="utf-8")
            print(f"Updated {target}")


if __name__ == "__main__":
    main()
