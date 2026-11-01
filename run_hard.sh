#!/bin/bash
# name onTime rate attackStart bottleneckMbps
scenarios=(
"h1 0.05 4 8 5"
"h2 0.05 6 8 5"
"h3 0.1 5 8 5"
"h4 0.2 10 8 8"
"h5 0.1 8 8 8"
"h6 0.2 10 8 3"
"h7 0.2 10 100 8"
"h8 0.2 10 100 3"
"h9 0.2 10 100 10"
"h10 0.1 6 7 8"
)
for s in "${scenarios[@]}"; do
  set -- $s
  echo "Running $1 ..."
  ./ns3 run "lowrate-test --prefix=$1 --onTime=$2 --rate=$3 --attackStart=$4 --bw=$5"
done
echo "All done"
