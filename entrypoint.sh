#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
