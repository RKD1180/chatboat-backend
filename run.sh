#!/bin/bash
echo "Starting Chatbot Backend..."
echo ""
echo "Make sure you have installed dependencies:"
echo "pip install -r requirements.txt"
echo ""
cd "$(dirname "$0")"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
