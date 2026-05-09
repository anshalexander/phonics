#!/bin/bash
# Phonics Playground launcher
# Double-click this file in Finder to start the local server and open the
# artifact in your browser. Solves the file:// audio-loading problem.
#
# First time only: in Terminal, run
#   chmod +x "$(dirname "$0")/start.command"
# (or just: chmod +x start.command  if you cd into this folder)

set -e
cd "$(dirname "$0")"

PORT=8765
URL="http://localhost:${PORT}/SATPIN_StoryMode.html"

# Pick a Python interpreter
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
done
if [ -z "$PY" ]; then
  echo "ERROR: Python is not installed. macOS usually comes with python3."
  echo "Install it with:  xcode-select --install"
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

# Kill only PYTHON listeners on the port (avoids SIGKILLing unrelated
# apps that happen to be on 8765 — a dev server, a Node process, etc).
lsof -ti tcp:${PORT} -sTCP:LISTEN 2>/dev/null | while read pid; do
  if ps -p "$pid" -o comm= 2>/dev/null | grep -qi python; then
    kill "$pid" 2>/dev/null || true
  fi
done

echo
echo "================================================================"
echo "  Phonics Playground server"
echo "  Open your browser at:  ${URL}"
echo "  (it should open automatically in 2 seconds)"
echo "  Leave this window open while using the page."
echo "  Close this window or press Ctrl+C to stop."
echo "================================================================"
echo

# Open browser after a short delay
( sleep 2; open "$URL" ) &

# Start the server (foreground so closing the window stops it).
# Don't `exec` — if the bind fails (port held by another process,
# TIME_WAIT after the kill above) we want to keep the Terminal open
# so the user can read the error instead of having the window vanish.
"$PY" -m http.server "${PORT}"
status=$?
if [ "$status" -ne 0 ]; then
  echo
  echo "Server exited with status ${status}."
  echo "If the message above mentions 'Address already in use', another"
  echo "app is holding port ${PORT}. Try a different terminal window or"
  echo "wait ~30s for the OS to release it."
  read -n 1 -s -r -p "Press any key to close..."
fi
exit $status
