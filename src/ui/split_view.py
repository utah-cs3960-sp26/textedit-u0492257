"""Split view manager for editor panes."""

from PyQt6.QtWidgets import QSplitter, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QTimer
from PyQt6.QtGui import QPainter, QColor

from ui.tab_widget import TabWidget


class DropZoneOverlay(QWidget):
    """Overlay widget that shows drop zones when dragging files."""
    
    zone_selected = pyqtSignal(str)  # 'top', 'bottom', 'left', 'right'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        self._active_zone = None
        self._visible = False
    
    def show_zones(self):
        """Show the drop zone overlay."""
        self._visible = True
        self.raise_()
        self.show()
        self.update()
    
    def hide_zones(self):
        """Hide the drop zone overlay."""
        self._visible = False
        self._active_zone = None
        self.hide()
    
    def get_zone_at(self, pos):
        """Determine which zone the position is in based on which half the cursor is closest to."""
        rect = self.rect()
        w, h = rect.width(), rect.height()
        x, y = pos.x(), pos.y()
        
        dist_top = y
        dist_bottom = h - y
        dist_left = x
        dist_right = w - x
        
        min_dist = min(dist_top, dist_bottom, dist_left, dist_right)
        
        if min_dist == dist_top:
            return 'top'
        elif min_dist == dist_bottom:
            return 'bottom'
        elif min_dist == dist_left:
            return 'left'
        else:
            return 'right'
    
    def get_zone_rect(self, zone):
        """Get the rectangle for a specific zone - highlights half the window."""
        rect = self.rect()
        w, h = rect.width(), rect.height()
        
        if zone == 'top':
            return QRect(0, 0, w, h // 2)
        elif zone == 'bottom':
            return QRect(0, h // 2, w, h // 2)
        elif zone == 'left':
            return QRect(0, 0, w // 2, h)
        elif zone == 'right':
            return QRect(w // 2, 0, w // 2, h)
        return QRect()
    
    def set_active_zone(self, zone):
        """Set the currently highlighted zone."""
        if self._active_zone != zone:
            self._active_zone = zone
            self.update()
    
    def paintEvent(self, event):
        if not self._visible:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._active_zone:
            zone_rect = self.get_zone_rect(self._active_zone)
            painter.fillRect(zone_rect, QColor(0, 170, 170, 80))
            painter.setPen(QColor(0, 170, 170, 200))
            painter.drawRect(zone_rect)


class SplitPane(QWidget):
    """A pane containing a tab widget with drop zone support."""
    
    split_requested = pyqtSignal(object, str, str)  # pane, direction, file_path
    split_with_tab_requested = pyqtSignal(object, str, object, int)  # pane, direction, source_tab_widget, tab_index
    close_requested = pyqtSignal(object)  # pane
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.tab_widget = TabWidget()
        self.tab_widget.last_tab_closed.connect(self._on_last_tab_closed)
        layout.addWidget(self.tab_widget)
        
        self.drop_overlay = DropZoneOverlay(self)
        self.drop_overlay.hide()
    
    def _on_last_tab_closed(self):
        """Handle when the last tab in this pane is closed."""
        self.close_requested.emit(self)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.drop_overlay.setGeometry(self.rect())
    
    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasUrls() or mime.hasText() or mime.hasFormat("application/x-tab-index"):
            event.acceptProposedAction()
            self.drop_overlay.show_zones()
    
    def dragMoveEvent(self, event):
        zone = self.drop_overlay.get_zone_at(event.position().toPoint())
        self.drop_overlay.set_active_zone(zone)
        event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        self.drop_overlay.hide_zones()
    
    def dropEvent(self, event):
        zone = self.drop_overlay.get_zone_at(event.position().toPoint())
        self.drop_overlay.hide_zones()
        
        mime = event.mimeData()
        
        if mime.hasFormat("application/x-tab-index"):
            tab_index = int(mime.data("application/x-tab-index").data().decode())
            source = event.source()
            if source and hasattr(source, 'parent'):
                source_tab_widget = source.parent()
                if zone:
                    self.split_with_tab_requested.emit(self, zone, source_tab_widget, tab_index)
            event.acceptProposedAction()
            return
        
        file_path = None
        if mime.hasUrls():
            urls = mime.urls()
            if urls:
                file_path = urls[0].toLocalFile()
        elif mime.hasText():
            file_path = mime.text()
        
        if file_path and zone:
            self.split_requested.emit(self, zone, file_path)
        elif file_path:
            self.tab_widget.open_file(file_path)
        
        event.acceptProposedAction()


class SplitViewManager(QWidget):
    """Manages split editor panes with original size restoration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_size = None
        self._is_split = False
        self._panes = []
        self._splitters = []
        
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        self._root_pane = self._create_pane()
        self._main_layout.addWidget(self._root_pane)
        self._panes.append(self._root_pane)
    
    def _create_pane(self):
        """Create a new split pane."""
        pane = SplitPane()
        pane.split_requested.connect(self._handle_split)
        pane.split_with_tab_requested.connect(self._handle_tab_split)
        pane.close_requested.connect(self._handle_pane_close)
        return pane
    
    @property
    def original_size(self):
        """Get the stored original window size."""
        return self._original_size
    
    @property
    def is_split(self):
        """Check if currently in split view mode."""
        return self._is_split
    
    @property
    def tab_widget(self):
        """Get the primary tab widget (for compatibility)."""
        if self._panes:
            return self._panes[0].tab_widget
        return None
    
    @property
    def current_editor(self):
        """Get the current editor from the focused pane."""
        if self._panes:
            return self._panes[0].tab_widget.current_editor
        return None
    
    @property
    def current_document(self):
        """Get the current document from the focused pane."""
        if self._panes:
            return self._panes[0].tab_widget.current_document
        return None
    
    def store_original_size(self, size):
        """Store the original window size before splitting."""
        if self._original_size is None:
            self._original_size = QSize(size)
    
    def _handle_split(self, source_pane, direction, file_path):
        """Handle a split request from a pane."""
        if not self._is_split:
            window = self.window()
            if window:
                self.store_original_size(window.size())
        
        new_pane = self._create_pane()
        self._panes.append(new_pane)
        
        if file_path:
            new_pane.tab_widget.open_file(file_path)
        
        if direction in ('left', 'right'):
            orientation = Qt.Orientation.Horizontal
            total_size = source_pane.width()
        else:
            orientation = Qt.Orientation.Vertical
            total_size = source_pane.height()
        
        half_size = total_size // 2
        
        splitter = QSplitter(orientation)
        self._splitters.append(splitter)
        
        parent = source_pane.parent()
        if isinstance(parent, QSplitter):
            index = parent.indexOf(source_pane)
            source_pane.setParent(None)
            
            if direction in ('left', 'top'):
                splitter.addWidget(new_pane)
                splitter.addWidget(source_pane)
            else:
                splitter.addWidget(source_pane)
                splitter.addWidget(new_pane)
            
            parent.insertWidget(index, splitter)
        else:
            self._main_layout.removeWidget(source_pane)
            source_pane.setParent(None)
            
            if direction in ('left', 'top'):
                splitter.addWidget(new_pane)
                splitter.addWidget(source_pane)
            else:
                splitter.addWidget(source_pane)
                splitter.addWidget(new_pane)
            
            self._main_layout.addWidget(splitter)
        
        QTimer.singleShot(0, lambda: splitter.setSizes([half_size, half_size]))
        self._is_split = True
    
    def _handle_tab_split(self, source_pane, direction, source_tab_widget, tab_index):
        """Handle a split request from dragging a tab."""
        if not self._is_split:
            window = self.window()
            if window:
                self.store_original_size(window.size())
        
        tab = source_tab_widget._tabs[tab_index] if 0 <= tab_index < len(source_tab_widget._tabs) else None
        if not tab:
            return
        
        content = tab.editor.toPlainText()
        file_path = tab.document.file_path
        is_modified = tab.document.is_modified
        
        new_pane = self._create_pane()
        self._panes.append(new_pane)
        
        new_tab = new_pane.tab_widget.current_tab()
        new_tab.editor.setPlainText(content)
        new_tab.document.file_path = file_path
        new_tab.document.is_modified = is_modified
        new_pane.tab_widget._update_tab_title(new_tab)
        
        source_tab_widget._close_tab(tab)
        
        if direction in ('left', 'right'):
            orientation = Qt.Orientation.Horizontal
            total_size = source_pane.width()
        else:
            orientation = Qt.Orientation.Vertical
            total_size = source_pane.height()
        
        half_size = total_size // 2
        
        splitter = QSplitter(orientation)
        self._splitters.append(splitter)
        
        parent = source_pane.parent()
        if isinstance(parent, QSplitter):
            index = parent.indexOf(source_pane)
            source_pane.setParent(None)
            
            if direction in ('left', 'top'):
                splitter.addWidget(new_pane)
                splitter.addWidget(source_pane)
            else:
                splitter.addWidget(source_pane)
                splitter.addWidget(new_pane)
            
            parent.insertWidget(index, splitter)
        else:
            self._main_layout.removeWidget(source_pane)
            source_pane.setParent(None)
            
            if direction in ('left', 'top'):
                splitter.addWidget(new_pane)
                splitter.addWidget(source_pane)
            else:
                splitter.addWidget(source_pane)
                splitter.addWidget(new_pane)
            
            self._main_layout.addWidget(splitter)
        
        QTimer.singleShot(0, lambda: splitter.setSizes([half_size, half_size]))
        self._is_split = True
    
    def close_pane(self, pane):
        """Close a split pane and potentially restore original size."""
        if pane not in self._panes or len(self._panes) <= 1:
            return False
        
        self._panes.remove(pane)
        
        parent = pane.parent()
        pane.setParent(None)
        pane.deleteLater()
        
        if isinstance(parent, QSplitter):
            if parent.count() == 1:
                remaining = parent.widget(0)
                grandparent = parent.parent()
                
                if isinstance(grandparent, QSplitter):
                    index = grandparent.indexOf(parent)
                    remaining.setParent(None)
                    parent.setParent(None)
                    grandparent.insertWidget(index, remaining)
                else:
                    remaining.setParent(None)
                    parent.setParent(None)
                    self._main_layout.addWidget(remaining)
                
                if parent in self._splitters:
                    self._splitters.remove(parent)
                parent.deleteLater()
        
        if len(self._panes) == 1:
            self._is_split = False
            self._restore_original_size()
            return True
        
        return True
    
    def _handle_pane_close(self, pane):
        """Handle close request from a pane."""
        self.close_pane(pane)
    
    def _restore_original_size(self):
        """Restore window to original size after closing all splits."""
        if self._original_size is not None:
            window = self.window()
            if window:
                window.resize(self._original_size)
            self._original_size = None
    
    def close_all_splits(self):
        """Close all split panes except the first one."""
        while len(self._panes) > 1:
            self.close_pane(self._panes[-1])
    
    def split_count(self):
        """Return the number of active panes."""
        return len(self._panes)
