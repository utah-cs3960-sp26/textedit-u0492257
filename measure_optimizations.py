#!/usr/bin/env python3
"""
Measure performance improvements from optimizations.
Run this after each optimization phase.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt6.QtCore import QTimer


def measure_file_load(file_path, window):
    """Measure file load time and peak frame time."""
    start_time = time.time()
    window.tab_widget.open_file(file_path)
    
    # Process events to complete rendering
    app = QApplication.instance()
    for _ in range(10):
        app.processEvents()
        time.sleep(0.02)
    
    elapsed = time.time() - start_time
    
    if window.frame_timer_widget and window.frame_timer_widget.is_visible():
        timer = window.frame_timer_widget.timer
        return {
            'elapsed': elapsed,
            'max_frame': timer.max_frame_ms,
            'avg_frame': timer.avg_frame_ms,
            'frame_count': timer._frame_count
        }
    return {'elapsed': elapsed, 'max_frame': 0, 'avg_frame': 0, 'frame_count': 0}


def measure_scroll(window, lines=100):
    """Measure scroll performance."""
    editor = window.editor
    if not editor:
        return None
    
    if window.frame_timer_widget and window.frame_timer_widget.is_visible():
        window.frame_timer_widget.reset()
    
    cursor = editor.textCursor()
    start_time = time.time()
    
    app = QApplication.instance()
    for i in range(lines):
        cursor.movePosition(cursor.MoveOperation.Down)
        editor.setTextCursor(cursor)
        if i % 10 == 0:
            app.processEvents()
    
    elapsed = time.time() - start_time
    
    if window.frame_timer_widget and window.frame_timer_widget.is_visible():
        timer = window.frame_timer_widget.timer
        return {
            'elapsed': elapsed,
            'max_frame': timer.max_frame_ms,
            'avg_frame': timer.avg_frame_ms
        }
    return {'elapsed': elapsed, 'max_frame': 0, 'avg_frame': 0}


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Enable frame timer
    window.toggle_frame_timer()
    
    test_files = [
        ("small.txt", 300),
        ("medium.txt", 10000),
        ("large.txt", 1000000)
    ]
    
    print("\n" + "="*70)
    print("PERFORMANCE MEASUREMENT - AFTER OPTIMIZATIONS")
    print("="*70 + "\n")
    
    results = {}
    
    for file_name, lines in test_files:
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"Skipping {file_name} (not found)")
            continue
        
        print(f"Testing {file_name} ({lines:,} lines)...")
        
        # File load
        print("  Loading file...")
        window.frame_timer_widget.reset()
        load_result = measure_file_load(str(file_path), window)
        print(f"    Load time: {load_result['elapsed']:.3f}s")
        print(f"    Max frame: {load_result['max_frame']:.2f}ms")
        print(f"    Avg frame: {load_result['avg_frame']:.2f}ms")
        
        # Scroll
        print("  Scrolling 100 lines...")
        scroll_result = measure_scroll(window, 100)
        print(f"    Scroll time: {scroll_result['elapsed']:.3f}s")
        print(f"    Max frame: {scroll_result['max_frame']:.2f}ms")
        print(f"    Avg frame: {scroll_result['avg_frame']:.2f}ms")
        
        results[file_name] = {
            'load': load_result,
            'scroll': scroll_result
        }
        
        # Close tab
        window.tab_widget._close_tab(window.tab_widget.current_tab())
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    for file_name, data in results.items():
        print(f"\n{file_name}:")
        print(f"  Load:  {data['load']['elapsed']:.3f}s (max: {data['load']['max_frame']:.2f}ms)")
        print(f"  Scroll: {data['scroll']['elapsed']:.3f}s (max: {data['scroll']['max_frame']:.2f}ms)")
    
    window.close()


if __name__ == "__main__":
    main()
