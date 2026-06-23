#!/usr/bin/env bash

cd /home/kris/quant-platfor
source venv/bin/activate
PYTHONPATH=. python backtests/run_walk_forward.py