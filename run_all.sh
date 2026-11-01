#!/bin/bash
# Format: name onTime rate attackStart
# attackStart=100 means the attack never happens (pure normal run)
scenarios=(
"s1 0.1 8 8"
"s2 0.2 10 8"
"s3 0.3 10 8"
"s4 0.2 6 6"
"s5 0.1 12 10"
"s6 0.4 8 8"
"s7 0.2 10 100"
"s8 0.2 10 100"
"s9 0.15 9 7"
"s10 0.25 11 9"
)

for s in "${scenarios[@]}"; do
  set -- $s
  echo "Running $1 ..."
  ./ns3 run "lowrate-test --prefix=$1 --onTime=$2 --rate=$3 --attackStart=$4"
done
echo "All done"
