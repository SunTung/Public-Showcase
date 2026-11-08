#!/usr/bin/env bash
set -euo pipefail
APK="公開展示/cl_Taiwankeyin/AndroidMobile/app/build/outputs/apk/debug/app-debug.apk"
PACKAGE="tw.cell.taiwankeyin.alpha5test"
adb install -r "$APK"
adb logcat -c
adb shell am start -W -n "$PACKAGE/tw.cell.taiwankeyin.android.ImeProbeActivity"
# The activity posts its Android SQLite + real EditText.InputConnection test to the UI thread.
for n in $(seq 1 15); do
  LOGS="$(adb logcat -d -s CELL_IME_PROBE:D '*:S' || true)"
  if printf '%s' "$LOGS" | grep -q "PASS real EditText InputConnection"; then
    echo "$LOGS"; echo 'ANDROID EDITOR + SQLITE SMOKE PASS'; exit 0
  fi
  if printf '%s' "$LOGS" | grep -q "FAIL real Android editor/SQLite integration"; then
    echo "$LOGS"; echo 'ANDROID EDITOR + SQLITE SMOKE FAIL' >&2; exit 1
  fi
  sleep 2
done
adb logcat -d -s CELL_IME_PROBE:D '*:S' || true
echo 'ANDROID EDITOR + SQLITE SMOKE TIMEOUT' >&2
exit 1
