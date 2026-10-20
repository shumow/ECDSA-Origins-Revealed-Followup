#!/bin/bash
# Factor b for the 19 viable candidates, smallest first. One msieve run per value, own directory.
cd .
sort -k5 -n b_list.txt | while read run idx lab pbits b; do
  d="work_${run}_${idx}"; mkdir -p "$d"; cd "$d"
  rm -f msieve.dat msieve.fb msieve.log
  start=$(date +%s)
  msieve -q -t 2 "$b" > out.txt 2>&1
  end=$(date +%s)
  echo "DONE $run $idx $lab $(( end - start ))s" >> ../progress.txt
  cd ..
done
echo "ALL_DONE" >> progress.txt
