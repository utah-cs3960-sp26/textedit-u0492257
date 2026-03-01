"""Find and Replace dialog for the text editor."""

import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


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
        """Replace all occurrences with frame timing."""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.warning(self, "Replace", "Enter text to find.")
            return
        
        doc_text = self.editor.toPlainText()
        match_count = doc_text.count(search_text)
        
        if match_count == 0:
            QMessageBox.information(self, "Replace", f"No matches found for '{search_text}'.")
            return
        
        # Reset frame timer if available
        if self.frame_timer_widget and self.frame_timer_widget.is_visible():
            self.frame_timer_widget.reset()
        
        # Perform replacement with timing
        from PyQt6.QtWidgets import QApplication
        
        start_time = time.time()
        
        # Do replacement
        new_text = doc_text.replace(search_text, replace_text)
        
        # Time the setPlainText operation
        set_text_start = time.time()
        self.editor.setPlainText(new_text)
        set_text_time = (time.time() - set_text_start) * 1000
        
        # Force repaint and process events to capture render frames
        for _ in range(10):
            QApplication.processEvents()
            time.sleep(0.001)
        
        elapsed = time.time() - start_time
        
        # Record the setText operation as a frame if no frames were captured
        if self.frame_timer_widget and self.frame_timer_widget.is_visible():
            timer = self.frame_timer_widget.timer
            # If no frames were captured by paint events, record setText time
            if timer._frame_count == 0:
                timer.record_frame(set_text_time)
        
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
