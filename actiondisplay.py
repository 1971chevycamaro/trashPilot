#!/usr/bin/env python3
import class_messaging as messaging
import sys

def main():
    sm = messaging.SubMaster('modelV2')
    max_force = .01  # max curvature for full scale
    bar_width = 50
    while True:
        if sm.updated():
            curv = sm.data()['action'][0]
            ratio = max(-1.0, min(1.0, curv / max_force))
            pos = int((ratio + 1) / 2 * bar_width)
            bar = " " * bar_width
            bar = bar[:pos] + "█" + bar[pos + 1:]
            sys.stdout.write(f"\r[{bar}] {curv:+.3f}")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
