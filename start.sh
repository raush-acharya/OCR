#!/usr/bin/env bash

# Install Tesseract at runtime
apt-get update && apt-get install -y tesseract-ocr

# Start the FastAPI server
uvicorn App:app --host=0.0.0.0 --port=8000
