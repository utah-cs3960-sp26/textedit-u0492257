#!/usr/bin/env python3
"""Performance measurement harness for the text editor."""

import time
import os
import sys
import psutil
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from ui.main_window import MainWindow


class PerformanceBenchmark:
    """Benchmark suite for text editor performance."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.results = {}
        self.process = psutil.Process(os.getpid())
    
    def measure_file_open(self, file_path):
        """Measure frame time during file open."""
        print(f"\n=== Testing file open: {file_path} ===")
        
        # Get initial memory
        mem_before = self.process.memory_info().rss / (1024 * 1024)  # MB
        
        # Clear and reset frame timer
        self.window.frame_timer_widget.reset()
        self.window.frame_timer_widget.show()
        self.window.frame_timer_widget._visible = True
        
        # Open file
        start = time.time()
        self.window.tab_widget.open_file(file_path)
        
        # Process events
        self.app.processEvents()
        time.sleep(0.5)  # Let UI settle
        self.app.processEvents()
        
        elapsed = time.time() - start
        
        # Get memory after
        mem_after = self.process.memory_info().rss / (1024 * 1024)  # MB
        
        # Get frame stats
        timer = self.window.frame_timer_widget.timer
        print(f"  File open time: {elapsed:.3f}s")
        print(f"  Max frame time: {timer.max_frame_ms:.2f} ms")
        print(f"  Avg frame time: {timer.avg_frame_ms:.2f} ms")
        print(f"  Frame count: {timer._frame_count}")
        print(f"  Memory before: {mem_before:.1f} MB")
        print(f"  Memory after: {mem_after:.1f} MB")
        print(f"  Memory delta: {mem_after - mem_before:.1f} MB")
        
        return {
            'elapsed': elapsed,
            'max_frame_ms': timer.max_frame_ms,
            'avg_frame_ms': timer.avg_frame_ms,
            'frame_count': timer._frame_count,
            'memory_mb': mem_after
        }
    
    def measure_scrolling(self, lines_to_scroll=500):
        """Measure frame time during scrolling."""
        print(f"\n=== Testing scrolling ({lines_to_scroll} lines) ===")
        
        self.window.frame_timer_widget.reset()
        
        editor = self.window.editor
        if not editor:
            print("No editor found")
            return
        
        # Get current cursor block
        cursor = editor.textCursor()
        doc = editor.document()
        total_blocks = doc.blockCount()
        
        # Scroll down
        start = time.time()
        for i in range(min(lines_to_scroll, total_blocks - 1)):
            cursor.movePosition(cursor.MoveOperation.Down)
            editor.setTextCursor(cursor)
            self.app.processEvents()
        
        elapsed = time.time() - start
        
        timer = self.window.frame_timer_widget.timer
        print(f"  Scroll time: {elapsed:.3f}s")
        print(f"  Max frame time: {timer.max_frame_ms:.2f} ms")
        print(f"  Avg frame time: {timer.avg_frame_ms:.2f} ms")
        print(f"  Frame count: {timer._frame_count}")
        
        return {
            'elapsed': elapsed,
            'max_frame_ms': timer.max_frame_ms,
            'avg_frame_ms': timer.avg_frame_ms,
            'frame_count': timer._frame_count
        }
    
    def measure_find_replace(self, file_path, search_term, replace_term):
        """Measure frame time during find/replace."""
        print(f"\n=== Testing find/replace: '{search_term}' -> '{replace_term}' ===")
        
        self.window.frame_timer_widget.reset()
        
        editor = self.window.editor
        if not editor:
            print("No editor found")
            return
        
        # Get document text
        text = editor.toPlainText()
        
        # Count matches
        match_count = len(re.findall(search_term, text))
        print(f"  Matches found: {match_count}")
        
        # Measure replace time
        start = time.time()
        new_text = text.replace(search_term, replace_term)
        editor.setPlainText(new_text)
        
        self.app.processEvents()
        time.sleep(0.5)
        self.app.processEvents()
        
        elapsed = time.time() - start
        
        timer = self.window.frame_timer_widget.timer
        print(f"  Replace time: {elapsed:.3f}s")
        print(f"  Max frame time: {timer.max_frame_ms:.2f} ms")
        print(f"  Avg frame time: {timer.avg_frame_ms:.2f} ms")
        print(f"  Frame count: {timer._frame_count}")
        
        return {
            'elapsed': elapsed,
            'max_frame_ms': timer.max_frame_ms,
            'avg_frame_ms': timer.avg_frame_ms,
            'frame_count': timer._frame_count,
            'match_count': match_count
        }
    
    def run_all_tests(self):
        """Run all performance tests."""
        test_files = [
            ("small.txt", 300),
            ("medium.txt", 10000),
            ("large.txt", 1000000)
        ]
        
        results = {}
        
        for file_name, expected_lines in test_files:
            file_path = Path(__file__).parent / file_name
            if not file_path.exists():
                print(f"Skipping {file_name} (file not found)")
                continue
            
            print(f"\n{'='*60}")
            print(f"Testing: {file_name} ({expected_lines:,} lines)")
            print(f"{'='*60}")
            
            # File open
            open_result = self.measure_file_open(str(file_path))
            
            # Scrolling
            scroll_result = self.measure_scrolling(100)
            
            # Find/replace
            find_result = self.measure_find_replace(str(file_path), "while", "for")
            
            results[file_name] = {
                'open': open_result,
                'scroll': scroll_result,
                'find_replace': find_result
            }
            
            # Close tab for next test
            self.window.tab_widget._close_tab(self.window.tab_widget.current_tab())
        
        return results


if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_tests()
    
    # Print summary
    print(f"\n{'='*60}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    for file_name, test_results in results.items():
        print(f"\n{file_name}:")
        print(f"  Open max frame: {test_results['open']['max_frame_ms']:.2f} ms")
        print(f"  Scroll max frame: {test_results['scroll']['max_frame_ms']:.2f} ms")
        print(f"  Find/Replace max frame: {test_results['find_replace']['max_frame_ms']:.2f} ms")
        print(f"  Find/Replace matches: {test_results['find_replace']['match_count']}")
        print(f"  Final memory: {test_results['open']['memory_mb']:.1f} MB")
