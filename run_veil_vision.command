#!/bin/sh
cd "$(dirname "$0")" || exit 1
# Prefer the native macOS Python already tested with this project.
for candidate in /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 python3; do
    if "$candidate" -c 'import sys, tkinter; raise SystemExit(sys.version_info < (3, 10))' 2>/dev/null; then
        exec "$candidate" main.py
    fi
done
printf '%s\n' 'Python 3.10 or newer with Tkinter is required. Install Python from python.org, then reopen this launcher.'
read answer
