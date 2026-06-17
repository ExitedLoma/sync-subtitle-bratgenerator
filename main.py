import time
import threading
import pyautogui
from pynput import keyboard
import pyperclip
import random

SPEED_FACTOR = 4
running = False

def to_seconds(time_str):
    h, m, s = time_str.split(":")
    s, ms = s.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def parse_srt(file_path):
    subtitles = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == '':
            i += 1
            continue
        if not line.isdigit():
            i += 1
            continue
        i += 1
        while i < len(lines) and lines[i].strip() == '':
            i += 1
        if i >= len(lines):
            break
        timestamp_line = lines[i].strip()
        if " --> " not in timestamp_line:
            i += 1
            continue
        start_str, end_str = timestamp_line.split(" --> ")
        start = to_seconds(start_str)
        end = to_seconds(end_str)
        i += 1
        text_lines = []
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped == '':
                i += 1
                break
            if stripped.isdigit():
                break
            text_lines.append(stripped)
            i += 1

        text = " ".join(text_lines).strip()
        subtitles.append((start, end, text))
    return subtitles

def type_text(text, scaled_start, scaled_end):
    global running
    duration = scaled_end - scaled_start
    total_chars = len(text)
    if total_chars == 0:
        return
    for i, char in enumerate(text):
        if not running:
            return
        target = scaled_start + (i / total_chars) * duration
        target += random.uniform(-0.01, 0.01)
        while running and time.time() < target:
            time.sleep(max(0, target - time.time()))
        pyperclip.copy(char)
        pyautogui.hotkey("ctrl", "v")

def play_subtitles(subtitles):
    global running, SPEED_FACTOR
    start_real = time.time()
    for start, end, text in subtitles:
        if not running:
            break
        real_start = start_real + start * SPEED_FACTOR
        real_end   = start_real + end   * SPEED_FACTOR
        time.sleep(0.070)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        while running and time.time() < real_start:
            time.sleep(max(0, real_start - time.time()))
        print(f"[{start} -> {end}] {text} (temps réel : {real_start-start_real:.2f} -> {real_end-start_real:.2f})")
        type_text(text, real_start, real_end)
    running = False
    print("Fin.")

def toggle():
    global running
    if running:
        running = False
        print("Arrêt.")
    else:
        print("Démarrage...")
        running = True
        subtitles = parse_srt("sub.srt")
        threading.Thread(target=play_subtitles, args=(subtitles,)).start()

def on_press(key):
    if key == keyboard.Key.f2:
        toggle()

print("Appuie sur F2 pour démarrer / arrêter.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()