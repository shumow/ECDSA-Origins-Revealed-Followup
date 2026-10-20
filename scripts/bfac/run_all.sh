#!/bin/bash
# Factor both P-224 signs and the other 15 coefficients in separate directories.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
work="${1:-$script_dir/../../results/bfac-work}"
mkdir -p "$work"
work="$(cd -- "$work" && pwd)"
"${PYTHON:-python}" "$script_dir/summarize.py" --write-inputs "$work/b_list.txt"
sort -k6 -n "$work/b_list.txt" | while read -r run idx root lab pbits b; do
  d="$work/work_${run}_${idx}_r${root}"
  if [ -e "$d" ]; then
    echo "Refusing to overwrite existing work directory: $d" >&2
    exit 1
  fi
  mkdir -p "$d"
  start=$(date +%s)
  (cd -- "$d" && msieve -q -t 2 "$b" > out.txt 2>&1)
  end=$(date +%s)
  echo "DONE $run $idx root$root $lab $(( end - start ))s" >> "$work/progress.txt"
done
echo "ALL_DONE" >> "$work/progress.txt"
"${PYTHON:-python}" "$script_dir/summarize.py" --from-msieve "$work"
