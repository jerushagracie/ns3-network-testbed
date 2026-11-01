#!/bin/bash
# name onTime rate
settings=(
"c1 0.1 8"
"c2 0.2 10"
"c3 0.3 10"
"c4 0.15 12"
)
for s in "${settings[@]}"; do
  set -- $s
  echo "Running $1 ..."
  ./ns3 run "lowrate-test --prefix=$1none --attackStart=100 --onTime=$2 --rate=$3" | grep THROUGHPUT > tp_$1_none.txt
  ./ns3 run "lowrate-test --prefix=$1nodef --onTime=$2 --rate=$3" | grep THROUGHPUT > tp_$1_nodef.txt
  ./ns3 run "lowrate-test --prefix=$1fw --fwLimit=2 --onTime=$2 --rate=$3" | grep THROUGHPUT > tp_$1_fw.txt
done
echo "Phase 1 done"
