#!/bin/sh
while true; do
  ./elgatoctl.py --load <<EOF
---
address: 10.0.0.13
port: 9123
name: Back
brightness: $(($RANDOM%100))
power: 1
temperature: 5000.0
EOF
  sleep $(($RANDOM%4))
done

