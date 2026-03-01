#!/usr/bin/env python3
"""
Automated performance testing script.
Measures frame times and records results to TIMING.md
"""

import time
import os
import sys
import psutil
import re
from pathlib import Path

# Test with the actual GUI
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QEventLoop
from PyQt6.QtGui import QKeySequence
from PyQt6.QtTest import QTest


def run_performance_tests():
    """Run all performance tests and record results."""
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    from ui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Let window stabilize
    app.processEvents()
    time.sleep(1)
    
    process = psutil.Process(os.getpid())
    results = {}
    
    test_cases = [
        ("small.txt", 300),
        ("medium.txt", 10000),
        ("large.txt", 1000000)
    ]
    
    print("\n" + "="*70)
    print("PERFORMANCE TESTING SUITE")
    print("="*70)
    
    # Test 1: Empty file (verify idle frame times < 16ms)
    print("\n[Test 0] Empty File (Idle Frame Verification)")
    print("-" * 70)
    
    window.frame_timer_widget.show()
    window.frame_timer_widget._visible = True
    window.frame_timer_widget.reset()
    
    # Wait and let it idle
    print("Measuring idle frames for 5 seconds...")
    start = time.time()
    while time.time() - start < 5:
        app.processEvents()
        time.sleep(0.01)
    
    idle_timer = window.frame_timer_widget.timer
    print(f"Idle Max Frame: {idle_timer.max_frame_ms:.2f} ms")
    print(f"Idle Avg Frame: {idle_timer.avg_frame_ms:.2f} ms")
    print(f"Idle Frame Count: {idle_timer._frame_count}")
    
    if idle_timer.max_frame_ms > 16:
        print("⚠️ WARNING: Idle frame times > 16ms suggests cursor blink is being timed!")
    else:
        print("✓ PASS: Idle frames are < 16ms")
    
    # Test each file
    for file_name, expected_lines in test_cases:
        file_path = Path(__file__).parent / file_name
        
        if not file_path.exists():
            print(f"\n⚠️  Skipping {file_name} (file not found)")
            continue
        
        print(f"\n[Test] {file_name} ({expected_lines:,} expected lines)")
        print("-" * 70)
        
        # A. File Open
        print(f"  A. File Open...")
        mem_before = process.memory_info().rss / (1024 * 1024)
        
        window.frame_timer_widget.reset()
        start_time = time.time()
        window.tab_widget.open_file(str(file_path))
        
        # Process events to render
        for _ in range(10):
            app.processEvents()
            time.sleep(0.05)
        
        open_time = time.time() - start_time
        mem_after = process.memory_info().rss / (1024 * 1024)
        
        timer = window.frame_timer_widget.timer
        results[f"{file_name}_open"] = {
            'max_frame_ms': timer.max_frame_ms,
            'avg_frame_ms': timer.avg_frame_ms,
            'elapsed': open_time,
            'memory_mb': mem_after
        }
        
        print(f"     Open time: {open_time:.3f}s")
        print(f"     Max frame: {timer.max_frame_ms:.2f} ms")
        print(f"     Avg frame: {timer.avg_frame_ms:.2f} ms")
        print(f"     Memory: {mem_after:.1f} MB (delta: {mem_after - mem_before:.1f} MB)")
        
        # B. Scrolling
        editor = window.editor
        if editor:
            print(f"  B. Scrolling (100 lines)...")
            window.frame_timer_widget.reset()
            
            cursor = editor.textCursor()
            start_time = time.time()
            
            for i in range(100):
                cursor.movePosition(cursor.MoveOperation.Down)
                editor.setTextCursor(cursor)
                app.processEvents()
            
            scroll_time = time.time() - start_time
            timer = window.frame_timer_widget.timer
            results[f"{file_name}_scroll"] = {
                'max_frame_ms': timer.max_frame_ms,
                'avg_frame_ms': timer.avg_frame_ms,
                'elapsed': scroll_time
            }
            
            print(f"     Scroll time: {scroll_time:.3f}s")
            print(f"     Max frame: {timer.max_frame_ms:.2f} ms")
            print(f"     Avg frame: {timer.avg_frame_ms:.2f} ms")
            
            # C. Find/Replace
            print(f"  C. Find/Replace (while → for)...")
            text = editor.toPlainText()
            match_count = text.count("while")
            
            window.frame_timer_widget.reset()
            start_time = time.time()
            
            new_text = text.replace("while", "for")
            editor.setPlainText(new_text)
            
            for _ in range(5):
                app.processEvents()
                time.sleep(0.05)
            
            replace_time = time.time() - start_time
            timer = window.frame_timer_widget.timer
            results[f"{file_name}_find_replace"] = {
                'max_frame_ms': timer.max_frame_ms,
                'avg_frame_ms': timer.avg_frame_ms,
                'elapsed': replace_time,
                'match_count': match_count
            }
            
            print(f"     Matches: {match_count}")
            print(f"     Replace time: {replace_time:.3f}s")
            print(f"     Max frame: {timer.max_frame_ms:.2f} ms")
            print(f"     Avg frame: {timer.avg_frame_ms:.2f} ms")
        
        # Close current tab for next test
        current_tab = window.tab_widget.current_tab()
        if current_tab:
            window.tab_widget._close_tab(current_tab)
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
    
    # Quit
    window.close()
    return results


if __name__ == "__main__":
    try:
        results = run_performance_tests()
        
        # Print summary
        print("\nSummary of Results:")
        for key, val in results.items():
            print(f"  {key}: {val}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
