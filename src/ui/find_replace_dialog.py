"""Find and Replace dialog for the text editor."""

import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor


class FindReplaceDialog(QDialog):
    """Simple Find and Replace dialog with frame timing."""
    
    def __init__(self, editor, parent=None, frame_timer_widget=None):
        super().__init__(parent)
        self.editor = editor
        self.frame_timer_widget = frame_timer_widget
        self.match_count = 0
        self._setup_ui()
        self.setWindowTitle("Find and Replace")
        self.resize(400, 150)
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Find row
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace row
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Buttons row
        button_layout = QHBoxLayout()
        
        find_btn = QPushButton("Find All")
        find_btn.clicked.connect(self._find_all)
        button_layout.addWidget(find_btn)
        
        replace_btn = QPushButton("Replace All")
        replace_btn.clicked.connect(self._replace_all)
        button_layout.addWidget(replace_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _find_all(self):
        """Find all occurrences."""
        search_text = self.find_input.text()
        if not search_text:
            QMessageBox.warning(self, "Find", "Enter text to find.")
            return
        
        doc_text = self.editor.toPlainText()
        self.match_count = doc_text.count(search_text)
        
        if self.match_count == 0:
            QMessageBox.information(self, "Find", f"No matches found for '{search_text}'.")
        else:
            QMessageBox.information(
                self, "Find",
                f"Found {self.match_count} match{'es' if self.match_count != 1 else ''}."
            )
    
    def _replace_all(self):
        """Replace all occurrences with batched QTextCursor replacements."""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.warning(self, "Replace", "Enter text to find.")
            return
        
        doc_text = self.editor.toPlainText()
        
        # Find all non-overlapping match positions
        spans = []
        search_len = len(search_text)
        start = 0
        while True:
            idx = doc_text.find(search_text, start)
            if idx == -1:
                break
            spans.append((idx, idx + search_len))
            start = idx + search_len
        
        match_count = len(spans)
        
        if match_count == 0:
            QMessageBox.information(self, "Replace", f"No matches found for '{search_text}'.")
            return
        
        # Reset frame timer if available
        if self.frame_timer_widget and self.frame_timer_widget.is_visible():
            self.frame_timer_widget.reset()
        
        # Reverse spans so we replace from end to start, preserving earlier offsets
        spans.reverse()
        
        # Store state for batch processing
        self._replace_spans = spans
        self._replace_text = replace_text
        self._replace_count = match_count
        self._replace_start_time = time.time()
        
        # Suspend syntax highlighter
        highlighter = self.editor.syntax_highlighter
        highlighter.suspend()
        
        # Disable undo/redo
        self.editor.setUndoRedoEnabled(False)
        
        # Start batch processing
        QTimer.singleShot(0, self._process_replace_batch)
    
    def _process_replace_batch(self):
        """Process a batch of replacements within a time budget."""
        BATCH_TIME_BUDGET = 0.008  # ~8ms per batch
        
        cursor = QTextCursor(self.editor.document())
        cursor.beginEditBlock()
        
        batch_start = time.time()
        while self._replace_spans and (time.time() - batch_start) < BATCH_TIME_BUDGET:
            start, end = self._replace_spans.pop()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(self._replace_text)
        
        cursor.endEditBlock()
        
        QApplication.processEvents()
        
        if self._replace_spans:
            # Schedule next batch
            QTimer.singleShot(0, self._process_replace_batch)
        else:
            # All replacements done — finalize
            self._finish_replace()
    
    def _finish_replace(self):
        """Finalize replace-all after all batches complete."""
        # Resume syntax highlighter
        highlighter = self.editor.syntax_highlighter
        highlighter.resume()
        
        # For large files, only highlight visible blocks instead of full rehighlight
        block_count = self.editor.blockCount()
        if block_count > 50000:
            first = self.editor.firstVisibleBlock()
            last_num = first.blockNumber() + 50
            highlighter.highlight_visible_blocks(first.blockNumber(), last_num)
        else:
            highlighter.rehighlight()
        
        # Re-enable undo/redo
        self.editor.setUndoRedoEnabled(True)
        
        elapsed = time.time() - self._replace_start_time
        match_count = self._replace_count
        
        # Record frame timing if no frames were captured
        if self.frame_timer_widget and self.frame_timer_widget.is_visible():
            timer = self.frame_timer_widget.timer
            if timer._frame_count == 0:
                timer.record_frame(elapsed * 1000)
        
        # Get frame stats
        timer_info = ""
        if self.frame_timer_widget and self.frame_timer_widget.is_visible():
            timer = self.frame_timer_widget.timer
            timer_info = (
                f"\n\nFrame Timing:\n"
                f"Max frame: {timer.max_frame_ms:.2f}ms\n"
                f"Avg frame: {timer.avg_frame_ms:.2f}ms\n"
                f"Total operation time: {elapsed:.3f}s"
            )
        
        QMessageBox.information(
            self, "Replace",
            f"Replaced {match_count} match{'es' if match_count != 1 else ''}." + timer_info
        )
