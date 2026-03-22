"""Frame timer widget for performance monitoring."""

import time
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor


class FrameTimer:
    """Tracks frame timing metrics, excluding idle time."""
    
    def __init__(self):
        """Initialize frame timer."""
        self.reset()
        self._last_frame_time = None
        self._idle_threshold = 0.050  # 50ms - frames longer than this are considered idle
        self._is_active = False
    
    def reset(self):
        """Reset all statistics."""
        self.last_frame_ms = 0.0
        self.avg_frame_ms = 0.0
        self.max_frame_ms = 0.0
        self._frame_times = []
        self._frame_count = 0
        self._total_frame_time = 0.0
        self._last_frame_time = None
    
    def start(self):
        """Start the timer (mark beginning of work)."""
        if not self._is_active:
            self._is_active = True
            self._last_frame_time = time.time()
    
    def end_frame(self):
        """End the current frame and record timing."""
        if not self._is_active or self._last_frame_time is None:
            return
        
        frame_time = (time.time() - self._last_frame_time) * 1000  # Convert to ms
        
        # Only record frame if it's not idle (e.g., cursor blink)
        # Idle frames are typically > 50ms with no user interaction
        if frame_time < self._idle_threshold:
            self.last_frame_ms = frame_time
            self._frame_times.append(frame_time)
            self._frame_count += 1
            self._total_frame_time += frame_time
            
            # Update max
            if frame_time > self.max_frame_ms:
                self.max_frame_ms = frame_time
            
            # Update average
            self.avg_frame_ms = self._total_frame_time / self._frame_count
    
    def mark_idle(self):
        """Mark that we're entering idle state (no more frame tracking until start() is called again)."""
        self._is_active = False
        self._last_frame_time = None
    
    def start_frame(self):
        """Start measuring a new frame."""
        self._last_frame_time = time.time()
        self._is_active = True
    
    def record_frame(self, frame_time_ms):
        """Record a frame time measurement."""
        self.last_frame_ms = frame_time_ms
        self._frame_times.append(frame_time_ms)
        self._frame_count += 1
        self._total_frame_time += frame_time_ms
        
        if frame_time_ms > self.max_frame_ms:
            self.max_frame_ms = frame_time_ms
        
        if self._frame_count > 0:
            self.avg_frame_ms = self._total_frame_time / self._frame_count


class FrameTimerWidget(QWidget):
    """Widget that displays frame timing information."""
    
    def __init__(self, parent=None):
        """Initialize the frame timer widget."""
        super().__init__(parent)
        self.timer = FrameTimer()
        self._visible = False
        self._setup_ui()
        self._update_display()
    
    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Create labels for frame metrics
        self.last_frame_label = QLabel("Last: 0.0 ms")
        self.avg_frame_label = QLabel("Avg: 0.0 ms")
        self.max_frame_label = QLabel("Max: 0.0 ms")
        
        # Set monospace font
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFamilies(["Menlo", "Courier New", "Consolas", "DejaVu Sans Mono"])
        font.setPointSize(9)
        
        for label in [self.last_frame_label, self.avg_frame_label, self.max_frame_label]:
            label.setFont(font)
            label.setStyleSheet(
                "color: #00FF00; background-color: #000000; padding: 2px;"
            )
            layout.addWidget(label)
        
        self.setLayout(layout)
        self.setStyleSheet(
            "QWidget { background-color: #000000; border: 1px solid #00FF00; }"
        )
    
    def _update_display(self):
        """Update the displayed frame metrics."""
        self.last_frame_label.setText(f"Last: {self.timer.last_frame_ms:.2f} ms")
        self.avg_frame_label.setText(f"Avg: {self.timer.avg_frame_ms:.2f} ms")
        self.max_frame_label.setText(f"Max: {self.timer.max_frame_ms:.2f} ms")
    
    def record_frame(self, frame_time_ms):
        """Record a frame time measurement."""
        self.timer.record_frame(frame_time_ms)
        self._update_display()
    
    def reset(self):
        """Reset all statistics."""
        self.timer.reset()
        self._update_display()
    
    def toggle_visibility(self):
        """Toggle visibility and reset statistics when hidden."""
        if self._visible:
            self.hide()
            self.reset()
            self._visible = False
        else:
            self.show()
            self.reset()
            self._visible = True
    
    def is_visible(self):
        """Check if timer is visible/active."""
        return self._visible
