"""Main text editor widget with line numbers."""

import time
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QFont, QPainter, QColor, QTextFormat
from PyQt6.QtCore import Qt, QRect, QSize

from editor.syntax_highlighter import SyntaxHighlighter


class LineNumberArea(QWidget):
    """Widget that displays line numbers alongside the editor."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class TextEditor(QPlainTextEdit):
    """Text editor widget with vintage terminal styling and line numbers."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        self.syntax_highlighter = SyntaxHighlighter(self.document())
        
        # Frame timing
        self._frame_timer_widget = None
        self._frame_start_time = None
        
        # Performance optimizations
        self._line_height_cache = {}  # Cache block heights
        self._cached_line_number_width = None
        self._cached_digit_count = None
        self._last_block_count = 0

        self._setup_appearance()
        self._connect_signals()
        self._update_line_number_area_width()
        
        # Disable line wrapping for consistent line height and fast scrolling
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    
    def _setup_appearance(self):
        """Configure the vintage terminal look."""
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFamilies(["Menlo", "Courier New", "Consolas", "DejaVu Sans Mono", "Liberation Mono"])
        font.setPointSize(12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
    
    def _connect_signals(self):
        """Connect signals for line number updates."""
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.updateRequest.connect(self._highlight_visible_on_scroll)
    
    def line_number_area_width(self):
        """Calculate the width needed for line numbers (cached)."""
        block_count = self.blockCount()
        digits = len(str(max(1, block_count)))
        
        # Only recalculate if block count changes
        if block_count != self._last_block_count or self._cached_digit_count != digits:
            self._cached_digit_count = digits
            self._last_block_count = block_count
            self._cached_line_number_width = 3 + self.fontMetrics().horizontalAdvance("9") * max(digits, 3)
        
        return self._cached_line_number_width if self._cached_line_number_width else 50
    
    def _update_line_number_area_width(self):
        """Update editor margins to accommodate line numbers."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy):
        """Scroll or repaint line number area as needed."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()
    
    def resizeEvent(self, event):
        """Resize line number area when editor is resized."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def _highlight_current_line(self):
        """Highlight the line where the cursor is."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(50, 50, 50)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def line_number_area_paint_event(self, event):
        """Paint the line numbers (optimized for visible lines only)."""
        self._start_frame_timing()
        
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(30, 30, 30))
        
        # Only paint lines in the event rect
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        
        font_height = self.fontMetrics().height()
        event_bottom = event.rect().bottom()
        event_top = event.rect().top()
        
        painter.setPen(QColor(100, 100, 100))
        area_width = self.line_number_area.width()
        
        # Only iterate through visible lines
        while block.isValid() and top <= event_bottom:
            if top + font_height >= event_top:  # Only paint if in view
                if block.isVisible():
                    number = str(block_number + 1)
                    painter.drawText(
                        0, top,
                        area_width - 5,
                        font_height,
                        Qt.AlignmentFlag.AlignRight,
                        number
                    )
            
            block = block.next()
            top += int(self.blockBoundingRect(block).height())
            block_number += 1
        
        self._end_frame_timing()
    
    def _highlight_visible_on_scroll(self, rect, dy):
        """Highlight visible blocks on scroll for large files with deferred highlighting."""
        if self.blockCount() <= 50000:
            return
        if not dy:
            return
        block = self.firstVisibleBlock()
        first_num = block.blockNumber()
        last_num = first_num + 50
        self.syntax_highlighter.highlight_visible_blocks(first_num, last_num)
    
    def set_syntax_language(self, language, rehighlight_now=True):
        """Set the syntax highlighting language."""
        self.syntax_highlighter.set_language(language, rehighlight_now=rehighlight_now)
    
    def set_frame_timer_widget(self, widget):
        """Set the frame timer widget for performance monitoring."""
        self._frame_timer_widget = widget
    
    def _start_frame_timing(self):
        """Start measuring frame time."""
        if self._frame_timer_widget and self._frame_timer_widget.is_visible():
            self._frame_start_time = time.time()
    
    def _end_frame_timing(self):
        """End frame timing and record the measurement."""
        if self._frame_start_time is not None and self._frame_timer_widget and self._frame_timer_widget.is_visible():
            frame_time_ms = (time.time() - self._frame_start_time) * 1000
            self._frame_timer_widget.record_frame(frame_time_ms)
            self._frame_start_time = None

    _BRACKET_PAIRS = {'(': ')', '[': ']', '{': '}'}
    _QUOTE_CHARS = {'"', "'"}
    _CLOSING_BRACKETS = {')', ']', '}'}
    
    def keyPressEvent(self, event):
        """Handle key press events with automatic indentation and pair matching."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._handle_enter_key()
            return
        
        text = event.text()
        if text:
            if text in self._BRACKET_PAIRS:
                self._insert_pair(text, self._BRACKET_PAIRS[text])
                return
            if text in self._QUOTE_CHARS:
                self._handle_quote(text)
                return
            if text in self._CLOSING_BRACKETS:
                if self._skip_if_next_char(text):
                    return
        
        if event.key() == Qt.Key.Key_Backspace:
            if self._handle_backspace_pair():
                return
        
        if event.key() == Qt.Key.Key_Tab:
            if self._handle_tab_jump():
                return
        
        super().keyPressEvent(event)
    
    def _insert_pair(self, opening: str, closing: str):
        """Insert an opening bracket and its matching closing bracket."""
        cursor = self.textCursor()
        cursor.insertText(opening + closing)
        cursor.movePosition(cursor.MoveOperation.Left)
        self.setTextCursor(cursor)
    
    def _handle_quote(self, quote: str):
        """Handle quote insertion with smart matching."""
        cursor = self.textCursor()
        doc = self.document()
        pos = cursor.position()
        
        if pos < doc.characterCount() - 1:
            next_char = doc.characterAt(pos)
            if next_char == quote:
                cursor.movePosition(cursor.MoveOperation.Right)
                self.setTextCursor(cursor)
                return
        
        cursor.insertText(quote + quote)
        cursor.movePosition(cursor.MoveOperation.Left)
        self.setTextCursor(cursor)
    
    def _skip_if_next_char(self, char: str) -> bool:
        """Skip over the next character if it matches, instead of inserting."""
        cursor = self.textCursor()
        doc = self.document()
        pos = cursor.position()
        
        if pos < doc.characterCount() - 1:
            next_char = doc.characterAt(pos)
            if next_char == char:
                cursor.movePosition(cursor.MoveOperation.Right)
                self.setTextCursor(cursor)
                return True
        return False
    
    def _handle_backspace_pair(self) -> bool:
        """Delete both brackets/quotes if backspace is pressed between an empty pair."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return False
        
        doc = self.document()
        pos = cursor.position()
        
        if pos == 0 or pos >= doc.characterCount():
            return False
        
        prev_char = doc.characterAt(pos - 1)
        next_char = doc.characterAt(pos)
        
        pairs = {**self._BRACKET_PAIRS, '"': '"', "'": "'"}
        
        if prev_char in pairs and pairs[prev_char] == next_char:
            cursor.movePosition(cursor.MoveOperation.Left)
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 2)
            cursor.removeSelectedText()
            return True
        
        return False
    
    def _handle_tab_jump(self) -> bool:
        """Jump cursor past closing bracket/quote if inside a pair."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return False
        
        doc = self.document()
        pos = cursor.position()
        
        if pos >= doc.characterCount():
            return False
        
        next_char = doc.characterAt(pos)
        
        if next_char in self._CLOSING_BRACKETS or next_char in self._QUOTE_CHARS:
            cursor.movePosition(cursor.MoveOperation.Right)
            self.setTextCursor(cursor)
            return True
        
        return False
    
    def _handle_enter_key(self):
        """Handle Enter key with bracket-aware automatic indentation."""
        cursor = self.textCursor()
        current_line = cursor.block().text()
        col = cursor.positionInBlock()
        
        text_before = current_line[:col]
        text_after = current_line[col:]
        
        base_indent = self._get_leading_whitespace(current_line)
        indent_unit = self._detect_indent_unit()
        
        has_unclosed = self._count_unclosed_brackets(text_before) > 0
        
        if has_unclosed:
            new_indent = base_indent + indent_unit
            
            stripped_after = text_after.lstrip()
            if stripped_after and stripped_after[0] in ')]}':
                cursor.insertText('\n' + new_indent + '\n' + base_indent)
                cursor.movePosition(cursor.MoveOperation.Up)
                cursor.movePosition(cursor.MoveOperation.EndOfLine)
                self.setTextCursor(cursor)
            else:
                cursor.insertText('\n' + new_indent)
        else:
            adjusted_indent = self._adjust_indent_for_closing(base_indent, text_after, indent_unit)
            cursor.insertText('\n' + adjusted_indent)
    
    def _get_leading_whitespace(self, line: str) -> str:
        """Extract leading whitespace from a line."""
        return line[:len(line) - len(line.lstrip())]
    
    def _detect_indent_unit(self) -> str:
        """Detect the indentation unit used in the document (tabs or spaces)."""
        doc = self.document()
        for i in range(doc.blockCount()):
            line = doc.findBlockByNumber(i).text()
            if line.startswith('\t'):
                return '\t'
            stripped = line.lstrip()
            if stripped and line != stripped:
                ws = line[:len(line) - len(stripped)]
                spaces = ws.replace('\t', '')
                if spaces:
                    space_count = len(spaces)
                    if space_count >= 2:
                        return ' ' * min(space_count, 4)
        return '    '
    
    def _count_unclosed_brackets(self, text: str) -> int:
        """Count net unclosed opening brackets in text."""
        bracket_pairs = {'(': ')', '[': ']', '{': '}'}
        closing_to_opening = {v: k for k, v in bracket_pairs.items()}
        
        stack = []
        in_string = None
        escape = False
        
        for char in text:
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char in '"\'`':
                if in_string == char:
                    in_string = None
                elif in_string is None:
                    in_string = char
                continue
            if in_string:
                continue
            if char in bracket_pairs:
                stack.append(char)
            elif char in closing_to_opening:
                if stack and stack[-1] == closing_to_opening[char]:
                    stack.pop()
        
        return len(stack)
    
    def _adjust_indent_for_closing(self, base_indent: str, text_after: str, indent_unit: str) -> str:
        """Adjust indent if text_after starts with closing bracket."""
        stripped = text_after.lstrip()
        if stripped and stripped[0] in ')]}':
            if base_indent.endswith(indent_unit):
                return base_indent[:-len(indent_unit)]
        return base_indent
