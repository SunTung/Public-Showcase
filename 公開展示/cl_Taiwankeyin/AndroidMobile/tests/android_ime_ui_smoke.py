#!/usr/bin/env python3
"""Real Android 35 IME UI regression: install the pilot, tap its actual keys, inspect EditText."""
import re
import subprocess
import time
import xml.etree.ElementTree as ET

PACKAGE = "tw.cell.taiwankeyin.englishfix"
IME = PACKAGE + "/tw.cell.taiwankeyin.android.TaiwanKeyinImeService"
ACTIVITY = PACKAGE + "/tw.cell.taiwankeyin.android.SettingsActivity"

def adb(*args, timeout=90):
    p = subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError("adb " + " ".join(args) + ": " + p.stdout + p.stderr)
    return p.stdout

def nodes():
    adb("shell", "uiautomator", "dump", "/sdcard/cell_ime_ui.xml")
    raw = adb("shell", "cat", "/sdcard/cell_ime_ui.xml")
    start = raw.find("<?xml")
    if start < 0:
        raise AssertionError("Android accessibility hierarchy unavailable: " + raw[:400])
    return list(ET.fromstring(raw[start:]).iter("node"))

def bounds(node):
    match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.attrib.get("bounds", ""))
    if not match:
        raise AssertionError("Node without screen bounds: " + str(node.attrib))
    x1,y1,x2,y2 = map(int, match.groups())
    return (x1+x2)//2, (y1+y2)//2

def tap_node(node):
    x,y = bounds(node)
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(0.35)

def wait_node(text, attempts=6):
    for i in range(attempts):
        snapshot = nodes()
        hits = [n for n in snapshot if n.attrib.get("text") == text
                and n.attrib.get("class") == "android.widget.Button"]
        if hits:
            return hits[-1]
        time.sleep(0.7)
    visible = [(n.attrib.get("class"),n.attrib.get("text")) for n in snapshot
               if n.attrib.get("text")]
    raise AssertionError("Missing IME button {!r}; visible: {}".format(text, visible[-70:]))

def tap(text):
    tap_node(wait_node(text))

def editor_text():
    editors = [n for n in nodes() if n.attrib.get("class") == "android.widget.EditText"]
    if not editors:
        raise AssertionError("No focused EditText in Android UI")
    return editors[-1].attrib.get("text", "")

def assert_text_suffix(suffix):
    actual = editor_text()
    if not actual.endswith(suffix):
        raise AssertionError("Expected editor to end with {!r}, got {!r}".format(suffix, actual))

def main():
    apk = "公開展示/cl_Taiwankeyin/AndroidMobile/app/build/outputs/apk/pinyinTest/app-pinyinTest.apk"
    adb("install", "-r", apk, timeout=120)
    # Android PackageManager/IME service registration can lag behind adb install.
    # Use the actual ID from InputMethodManager rather than guessing its component syntax.
    registered = None
    for attempt in range(20):
        available = adb("shell", "ime", "list", "-s")
        registered = next((line.strip() for line in available.splitlines()
                           if line.strip().startswith(PACKAGE + "/")
                           and "TaiwanKeyinImeService" in line), None)
        if registered:
            break
        time.sleep(1)
    if not registered:
        details = adb("shell", "dumpsys", "input_method")
        raise AssertionError("IME not registered after install. ime list -s: {!r}; dumpsys: {}".format(
            available, details[-3000:]))
    adb("shell", "ime", "enable", registered)
    adb("shell", "ime", "set", registered)
    adb("shell", "am", "start", "-W", "-n", ACTIVITY)
    time.sleep(2)
    # Scroll the SettingsActivity to its built-in typing field.
    size = adb("shell", "wm", "size")
    match = re.search(r"(\d+)x(\d+)", size)
    width,height = map(int,match.groups()) if match else (1080,2200)
    for _ in range(4):
        snapshot = nodes()
        editors = [n for n in snapshot if n.attrib.get("class") == "android.widget.EditText"]
        if editors:
            tap_node(editors[-1])
            break
        adb("shell", "input", "swipe", str(width//2),str(height*3//4),
            str(width//2),str(height//4),"350")
        time.sleep(0.5)
    else:
        raise AssertionError("SettingsActivity typing field unavailable")
    wait_node("ABC")
    tap("ABC")
    wait_node("中")
    tap("q"); tap("w")
    assert_text_suffix("qw")
    tap("中")
    wait_node("繁注")
    expected = ["繁注","簡注","繁拼","簡拼"]
    for current in expected:
        wait_node(current)
        tap("ABC")
        wait_node("中")
        tap("a")
        tap("中")
        wait_node(current)
        tap(current)
    wait_node("繁注")
    assert_text_suffix("qwaaaa")
    print("PASS: Android on-screen ABC input, four Chinese mode transitions, English from every mode")
if __name__ == "__main__":
    main()
