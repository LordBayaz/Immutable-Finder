#!/bin/bash

echo "Scanning running processes for files with the immutable bit set..."
for pid in /proc/[0-9]*; do
  pid=$(basename "$pid")
  if [[ "$pid" =~ ^[0-9]+$ ]]; then
    for fd in /proc/$pid/fd/*; do
      if [[ -L "$fd" ]]; then
        file=$(readlink -f "$fd")
        if [[ -e "$file" && "$(lsattr "$file" 2>/dev/null | awk '{print $1}')" =~ i ]]; then
          cmdline=$(tr '\0' ' ' < /proc/$pid/cmdline)
          echo "PID: $pid, Command: $cmdline, File: $file"
        fi
      fi
    done
  fi
done
echo "Scan complete."

