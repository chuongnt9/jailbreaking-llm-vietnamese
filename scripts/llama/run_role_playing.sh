#!/bin/bash
CHECKPOINT_DIR=../../models/.llama/checkpoints/Llama3.1-8B-Instruct
PYTHONPATH=$(git rev-parse --show-toplevel) torchrun ./role_playing.py $CHECKPOINT_DIR
