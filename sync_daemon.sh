#!/bin/bash
while true; do
  if [[ -n $(git status -s) ]]; then
    git add .
    git commit -m "Auto-Sync: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
  fi
  sleep 30
done
