#!/bin/bash

mkdir -p data/models/bert ||:
# Download Financal dataset pre-trained model
wget https://prosus-public.s3-eu-west-1.amazonaws.com/finbert/finbert-sentiment/pytorch_model.bin -O data/models/bert/pytorch_model.bin
