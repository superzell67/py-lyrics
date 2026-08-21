import sys
from time import sleep
import time
import os

os.system("cls")

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def print_lyrics():
    lines = [
        ("Let me show you how to move", 0.04),
        ("Let me show you how to get", 0.04),
        ("That bag", 0.05),
        ("You ain't never coming last", 0.04),
        ("Fuck", 0.03),
        ("Your man", 0.04),
        ("You know this gonna make them mad", 0.04),
        ("Break", 0.06),
        ("That back", 0.05),
        ("Then we make a film on cam", 0.04),
        ("Shake", 0.08),
        ("That ass", 0.08),
        ("Baby show them that you bad", 0.04),
    ]

    delays = [0.06, 0.30, 0.35, 0.50, 0.40, 0.20, 0.15, 0.20, 0.50, 0.20, 0.15, 0.15, 0.10]

    hide_cursor()

    for i, (line, char_delay) in enumerate(lines):
        for char in line:
            print(char, end='')
            sys.stdout.flush()
            sleep(char_delay)

        time.sleep(delays[i])
        print('')

print_lyrics()