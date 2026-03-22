#!/usr/bin/env python3
"""
Measure frame times for various editor operations.
Run with: .venv/bin/python measure_frame_times.py

This script automates timing measurements for:
- File open
- Scrolling (arrow key)
- Scrollbar jump
- Find and Replace All
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor

from ui.main_window import MainWindow


def measure_operation(name, func, iterations=1):
    """Measure an operation's time in ms."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    avg = sum(times) / len(times)
    max_t = max(times)
    return avg, max_t, times


def run_measurements():
    app = QApplication(sys.argv)
    
    files = {
        "small.txt": "small.txt",
        "medium.txt": "medium.txt",
        "large.txt": "large.txt",
    }
    
    results = {}
    
    for name, path in files.items():
        full_path = str(Path(__file__).parent / path)
        print(f"\n{'='*60}")
        print(f"Measuring: {name}")
        print(f"{'='*60}")
        
        # Measure file open
        window = MainWindow()
        window.show()
        app.processEvents()
        
        start = time.perf_counter()
        window.file_actions.open_file(full_path)
        app.processEvents()
        open_time = (time.perf_counter() - start) * 1000
        print(f"  File Open: {open_time:.2f}ms")
        
        editor = window.editor
        if not editor:
            print(f"  ERROR: No editor for {name}")
            continue
        
        # Process events to settle
        for _ in range(5):
            app.processEvents()
            time.sleep(0.01)
        
        # Measure scrolling (simulate scroll events)
        scroll_times = []
        for i in range(20):
            start = time.perf_counter()
            sb = editor.verticalScrollBar()
            sb.setValue(sb.value() + 10)
            app.processEvents()
            elapsed = (time.perf_counter() - start) * 1000
            scroll_times.append(elapsed)
        
        print(f"  Scroll Avg: {sum(scroll_times)/len(scroll_times):.2f}ms")
        print(f"  Scroll Max: {max(scroll_times):.2f}ms")
        dropped_scroll = sum(1 for t in scroll_times if t > 16)
        print(f"  Scroll Dropped Frames (>16ms): {dropped_scroll}/{len(scroll_times)}")
        
        # Measure scrollbar jump
        jump_times = []
        sb = editor.verticalScrollBar()
        max_val = sb.maximum()
        for i in range(10):
            target = int(max_val * (i / 10))
            start = time.perf_counter()
            sb.setValue(target)
            app.processEvents()
            elapsed = (time.perf_counter() - start) * 1000
            jump_times.append(elapsed)
        
        print(f"  Scrollbar Jump Avg: {sum(jump_times)/len(jump_times):.2f}ms")
        print(f"  Scrollbar Jump Max: {max(jump_times):.2f}ms")
        dropped_jump = sum(1 for t in jump_times if t > 16)
        print(f"  Scrollbar Jump Dropped Frames (>16ms): {dropped_jump}/{len(jump_times)}")
        
        # Measure find count
        doc_text = editor.toPlainText()
        match_count = doc_text.count("while")
        print(f"  Match count for 'while': {match_count}")
        
        # Store results
        results[name] = {
            "open": open_time,
            "scroll_avg": sum(scroll_times)/len(scroll_times),
            "scroll_max": max(scroll_times),
            "scroll_dropped": dropped_scroll,
            "jump_avg": sum(jump_times)/len(jump_times),
            "jump_max": max(jump_times),
            "jump_dropped": dropped_jump,
            "match_count": match_count,
        }
        
        window.close()
        app.processEvents()
    
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    for name, r in results.items():
        print(f"\n{name}:")
        print(f"  Open: {r['open']:.2f}ms")
        print(f"  Scroll: avg={r['scroll_avg']:.2f}ms max={r['scroll_max']:.2f}ms dropped={r['scroll_dropped']}")
        print(f"  Jump: avg={r['jump_avg']:.2f}ms max={r['jump_max']:.2f}ms dropped={r['jump_dropped']}")
        print(f"  Matches: {r['match_count']}")


if __name__ == "__main__":
    run_measurements()
