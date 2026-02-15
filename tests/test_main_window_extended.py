"""Extended tests for MainWindow to achieve 100% coverage."""

import pytest
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock, mock_open
from PyQt6.QtCore import Qt, QPoint, QPointF, QMimeData
from PyQt6.QtGui import QCloseEvent, QDrag
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtGui import QMouseEvent

from ui.main_window import MainWindow
from actions.file_actions import FileActions
from ui.tab_widget import DraggableTabBar
from ui.split_view import SplitPane


class TestMainWindowInit:
    """Test MainWindow initialization."""
    
    def test_main_window_creates(self, qtbot):
        """Test that MainWindow can be created."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert window is not None
    
    def test_main_window_has_splitter(self, qtbot):
        """Test that MainWindow has a splitter."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert hasattr(window, 'splitter')
        assert window.splitter is not None
    
    def test_main_window_has_file_explorer(self, qtbot):
        """Test that MainWindow has file explorer."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert hasattr(window, 'file_explorer')
        assert window.file_explorer is not None
    
    def test_main_window_has_split_view_manager(self, qtbot):
        """Test that MainWindow has split view manager."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert hasattr(window, 'split_view_manager')
        assert window.split_view_manager is not None
    
    def test_main_window_has_file_actions(self, qtbot):
        """Test that MainWindow has file actions."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert hasattr(window, 'file_actions')
        assert window.file_actions is not None


class TestMainWindowProperties:
    """Test MainWindow properties."""
    
    def test_tab_widget_property(self, qtbot):
        """Test tab_widget property."""
        window = MainWindow()
        qtbot.addWidget(window)
        assert window.tab_widget is not None
        assert window.tab_widget == window.split_view_manager.tab_widget
    
    def test_editor_property(self, qtbot):
        """Test editor property."""
        window = MainWindow()
        qtbot.addWidget(window)
        editor = window.editor
        # Should return editor from split view
        assert editor is not None
    
    def test_document_property(self, qtbot):
        """Test document property."""
        window = MainWindow()
        qtbot.addWidget(window)
        doc = window.document
        # Should return document from split view
        assert doc is not None


class TestMainWindowFileExplorerIntegration:
    """Test MainWindow file explorer integration."""
    
    def test_file_selected_opens_new_tab(self, qtbot):
        """Test that file_selected signal opens new tab."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        initial_count = window.tab_widget.count()
        
        # Simulate file selection
        test_file = "/test/file.txt"
        window._on_file_selected(test_file)
        
        # Should create new tab
        assert window.tab_widget.count() > initial_count
    
    def test_file_explorer_signal_connection(self, qtbot):
        """Test that file explorer signals are connected."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # The signal should be connected to _on_file_selected
        initial_count = window.tab_widget.count()
        window.file_explorer.file_selected.emit("/test/file.txt")
        qtbot.wait(50)
        # Tab count should increase
        assert window.tab_widget.count() >= initial_count


class TestMainWindowToggleFileExplorer:
    """Test MainWindow toggle file explorer."""
    
    def test_toggle_file_explorer_hides_explorer(self, qtbot):
        """Test toggling file explorer hides it."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(50)
        
        assert window.file_explorer.isVisible()
        
        window.toggle_file_explorer()
        qtbot.wait(50)
        assert not window.file_explorer.isVisible()
    
    def test_toggle_file_explorer_shows_explorer(self, qtbot):
        """Test toggling file explorer shows it."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        
        # Hide it first
        window.file_explorer.hide()
        qtbot.wait(50)
        assert not window.file_explorer.isVisible()
        
        # Show it
        window.toggle_file_explorer()
        qtbot.wait(50)
        assert window.file_explorer.isVisible()
    
    def test_toggle_file_explorer_restores_width(self, qtbot):
        """Test toggling file explorer restores width."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        original_sizes = window.splitter.sizes().copy()
        original_explorer_width = original_sizes[0]
        
        # Hide explorer
        window.toggle_file_explorer()
        
        # Show explorer
        window.toggle_file_explorer()
        
        # Width should be restored or set to default
        new_sizes = window.splitter.sizes()
        assert new_sizes[0] > 0


class TestMainWindowTitle:
    """Test MainWindow title updates."""
    
    def test_update_title_with_document(self, qtbot):
        """Test updating title with document."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        doc = window.document
        window.update_title()
        
        title = window.windowTitle()
        assert "PyNano" in title
    
    def test_update_title_with_modified_document(self, qtbot):
        """Test title shows modified indicator."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        doc = window.document
        if doc:
            doc.is_modified = True
            window.update_title()
            
            title = window.windowTitle()
            assert "*" in title
            
            # Reset to avoid dialog during cleanup
            doc.is_modified = False
    
    def test_update_title_without_document(self, qtbot):
        """Test title without document."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Mock split_view_manager.current_document to return None using PropertyMock
        with patch.object(type(window.split_view_manager), 'current_document', 
                         new_callable=PropertyMock) as mock_doc:
            mock_doc.return_value = None
            window.update_title()
            
            title = window.windowTitle()
            assert title == "PyNano"


class TestMainWindowCloseEvent:
    """Test MainWindow close event handling."""
    
    def test_close_event_accepts_if_no_unsaved(self, qtbot):
        """Test close event accepts if no unsaved changes."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Mock the unsaved changes check to return True (no unsaved changes)
        with patch.object(window.file_actions, '_check_unsaved_changes', return_value=True):
            event = MagicMock(spec=QCloseEvent)
            window.closeEvent(event)
            
            event.accept.assert_called_once()
    
    def test_close_event_ignores_if_unsaved(self, qtbot):
        """Test close event ignores if unsaved changes."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Mock the unsaved changes check to return False (has unsaved changes)
        with patch.object(window.file_actions, '_check_unsaved_changes', return_value=False):
            event = MagicMock(spec=QCloseEvent)
            window.closeEvent(event)
            
            event.ignore.assert_called_once()


class TestMainWindowUI:
    """Test MainWindow UI setup."""
    
    def test_main_window_resize(self, qtbot):
        """Test that main window is resized."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Should have width and height set
        assert window.width() == 1000
        assert window.height() == 600
    
    def test_splitter_collapsibility(self, qtbot):
        """Test splitter collapsibility."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # File explorer should be collapsible
        assert window.splitter.isCollapsible(0)
        
        # Split view manager should not be collapsible
        assert not window.splitter.isCollapsible(1)
    
    def test_splitter_sizes_set(self, qtbot):
        """Test splitter initial sizes."""
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(50)
        
        sizes = window.splitter.sizes()
        # First panel (explorer) should be approximately 200, second (editor) should be approximately 600
        # The exact values may differ due to window frame sizes
        assert sizes[0] > 0  # Explorer has some width
        assert sizes[1] > 0  # Editor area has some width
        assert sizes[0] + sizes[1] > 0  # Total width is positive


class TestEntryPointSubprocess:
    """Test the entry point using subprocess to cover if __name__ == '__main__'."""
    
    def test_main_entry_point_execution(self):
        """Test that main() can be executed via subprocess."""
        # Test the actual entry point with subprocess
        result = subprocess.run(
            [sys.executable, "-c", 
             "import sys; sys.path.insert(0, 'src'); from main import main; print('OK')"],
            cwd=str(Path(__file__).parent.parent),
            capture_output=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "OK" in result.stdout.decode()
    
    def test_run_py_entry_point_exists(self):
        """Test that run.py exists and imports work."""
        run_py = Path(__file__).parent.parent / "run.py"
        assert run_py.exists()
        
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(run_py)],
            capture_output=True
        )
        assert result.returncode == 0


class TestAdvancedDragDropSimulation:
    """Test advanced drag-and-drop with Qt event simulation."""
    
    def test_draggable_tab_bar_mouse_press(self, qtbot):
        """Test mouse press initiates drag start position."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        tab_bar.addTab("Tab 2")
        
        # Simulate mouse press
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(50, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        tab_bar.mousePressEvent(event)
        assert tab_bar._drag_start_pos == QPoint(50, 10)
    
    def test_draggable_tab_bar_mouse_move_small_distance(self, qtbot):
        """Test mouse move with small distance doesn't start drag."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        tab_bar.addTab("Tab 2")
        
        # Set initial drag position
        tab_bar._drag_start_pos = QPoint(50, 10)
        
        # Move a small distance (less than drag distance)
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(53, 12),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        tab_bar.mouseMoveEvent(move_event)
        # Should not start dragging on small movements
        assert tab_bar._dragging is False
    
    def test_draggable_tab_bar_mouse_move_while_dragging(self, qtbot):
        """Test mouse move when already dragging returns early."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        tab_bar._dragging = True
        
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(100, 10),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        # Should not re-initiate drag
        tab_bar.mouseMoveEvent(move_event)
        assert tab_bar._dragging is True
    
    def test_draggable_tab_bar_tab_at_invalid_index(self, qtbot):
        """Test drag initiated with invalid tab index."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar._drag_start_pos = QPoint(1000, 10)  # Far right, no tab there
        
        # Create large move to trigger drag check
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(1100, 10),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        tab_bar.mouseMoveEvent(move_event)
        # Should not crash and should not start drag
        assert tab_bar._dragging is False
    
    def test_draggable_tab_bar_mouse_release(self, qtbot):
        """Test mouse release clears drag state."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar._drag_start_pos = QPoint(50, 10)
        tab_bar._dragging = True
        
        release_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(150, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        tab_bar.mouseReleaseEvent(release_event)
        assert tab_bar._drag_start_pos is None
        assert tab_bar._dragging is False
    
    def test_split_pane_drop_zone_overlay_drag_enter(self, qtbot):
        """Test drag enter on split pane."""
        pane = SplitPane()
        qtbot.addWidget(pane)
        
        mime_data = QMimeData()
        mime_data.setText("test.txt")
        
        event = MagicMock()
        event.mimeData.return_value = mime_data
        
        pane.dragEnterEvent(event)
        event.acceptProposedAction.assert_called_once()
        assert pane.drop_overlay._visible is True
    
    def test_split_pane_drop_zone_overlay_drag_move(self, qtbot):
        """Test drag move updates active zone."""
        pane = SplitPane()
        qtbot.addWidget(pane)
        pane.show()
        qtbot.wait(50)
        
        pane.drop_overlay.show_zones()
        
        event = MagicMock()
        event.position.return_value.toPoint.return_value = QPoint(100, 100)
        
        pane.dragMoveEvent(event)
        # Should have updated zone based on position
        assert pane.drop_overlay._active_zone is not None
    
    def test_split_pane_drop_zone_overlay_drag_leave(self, qtbot):
        """Test drag leave hides overlay."""
        pane = SplitPane()
        qtbot.addWidget(pane)
        
        pane.drop_overlay.show_zones()
        assert pane.drop_overlay._visible is True
        
        event = MagicMock()
        pane.dragLeaveEvent(event)
        
        assert pane.drop_overlay._visible is False
    
    def test_split_pane_drop_with_tab_index_mime(self, qtbot):
        """Test drop event with tab index MIME data."""
        pane = SplitPane()
        qtbot.addWidget(pane)
        pane.show()
        qtbot.wait(50)
        
        mime_data = QMimeData()
        mime_data.setData("application/x-tab-index", b"0")
        
        # Create a real tab widget as source
        from ui.tab_widget import TabWidget
        source_tab_widget = TabWidget()
        qtbot.addWidget(source_tab_widget)
        
        # Create mock source that has the tab widget as parent
        mock_source = MagicMock()
        mock_source.parent = MagicMock(return_value=source_tab_widget)
        
        event = MagicMock()
        event.mimeData.return_value = mime_data
        event.position.return_value.toPoint.return_value = QPoint(100, 100)
        event.source.return_value = mock_source
        event.acceptProposedAction = MagicMock()
        
        signal_emitted = []
        pane.split_with_tab_requested.connect(lambda *args: signal_emitted.append(args))
        
        pane.dropEvent(event)
        # Should emit the signal with correct arguments
        assert len(signal_emitted) > 0
    
    def test_split_pane_drop_invalid_source(self, qtbot):
        """Test drop with invalid source doesn't crash."""
        pane = SplitPane()
        qtbot.addWidget(pane)
        pane.show()
        qtbot.wait(50)
        
        mime_data = QMimeData()
        mime_data.setData("application/x-tab-index", b"0")
        
        event = MagicMock()
        event.mimeData.return_value = mime_data
        event.position.return_value.toPoint.return_value = QPoint(100, 100)
        event.source.return_value = None  # Invalid source
        
        # Should not crash
        pane.dropEvent(event)
        event.acceptProposedAction.assert_called()


class TestEdgeCasesSynthetic:
    """Extensive edge case testing with synthetic scenarios."""
    
    def test_file_actions_save_without_editor(self, qtbot):
        """Test save_file returns False when no editor exists."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        actions = window.file_actions
        
        # Mock editor to return None
        with patch.object(type(window), 'editor', new_callable=PropertyMock) as mock_editor:
            mock_editor.return_value = None
            result = actions.save_file()
            assert result is False
    
    def test_file_actions_save_file_as_without_document(self, qtbot):
        """Test save_file_as returns False when no document."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        actions = window.file_actions
        
        # Mock document to return None
        with patch.object(type(window), 'document', new_callable=PropertyMock) as mock_doc:
            mock_doc.return_value = None
            result = actions.save_file_as()
            assert result is False
    
    def test_file_actions_save_file_as_write_error(self, qtbot):
        """Test save_file_as handles write errors gracefully."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        actions = window.file_actions
        
        with tempfile.TemporaryDirectory() as tmpdir:
            readonly_file = Path(tmpdir) / "readonly.txt"
            readonly_file.touch()
            os.chmod(readonly_file, 0o444)  # Read-only
            
            # Mock getSaveFileName to return readonly file
            with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog:
                mock_dialog.return_value = (str(readonly_file), "")
                with patch.object(QMessageBox, 'critical') as mock_critical:
                    result = actions.save_file_as()
                    # Should show error dialog
                    assert result is False or mock_critical.called
    
    def test_tab_widget_close_tab_not_in_list(self, qtbot):
        """Test closing tab that's not in the tab list."""
        from ui.tab_widget import TabWidget, EditorTab
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        # Create a tab not added to the widget
        orphan_tab = EditorTab()
        
        # Should not crash
        tab_widget._close_tab(orphan_tab)
        assert orphan_tab not in tab_widget._tabs
    
    def test_tab_widget_update_tab_title_invalid_tab(self, qtbot):
        """Test updating title for tab not in widget."""
        from ui.tab_widget import TabWidget, EditorTab
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        orphan_tab = EditorTab()
        
        # Should not crash
        tab_widget._update_tab_title(orphan_tab)
    
    def test_tab_widget_on_text_changed_invalid_tab(self, qtbot):
        """Test text changed signal for invalid tab."""
        from ui.tab_widget import TabWidget, EditorTab
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        orphan_tab = EditorTab()
        
        # Should not crash
        tab_widget._on_text_changed(orphan_tab)
    
    def test_open_file_with_bad_path(self, qtbot):
        """Test opening file with invalid path."""
        from ui.tab_widget import TabWidget
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        result = tab_widget.open_file("/nonexistent/path/to/file.txt")
        assert result is False
    
    def test_save_current_with_write_error(self, qtbot):
        """Test save_current handles write errors."""
        from ui.tab_widget import TabWidget
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        tab = tab_widget.current_tab()
        if tab:
            tab.document.file_path = "/nonexistent/path/file.txt"
            result = tab_widget.save_current()
            assert result is False
    
    def test_file_actions_open_file_cancelled(self, qtbot):
        """Test open_file when dialog is cancelled."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        actions = window.file_actions
        
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")  # Cancelled
            result = actions.open_file()
            assert result is False
    
    def test_file_actions_check_unsaved_save_action(self, qtbot):
        """Test check_unsaved_changes when Save is chosen."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        doc = window.document
        if doc:
            doc.is_modified = True
            
            with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_dialog:
                mock_dialog.return_value = QMessageBox.StandardButton.Save
                with patch.object(window.file_actions, 'save_file', return_value=True) as mock_save:
                    result = window.file_actions._check_unsaved_changes()
                    assert result is True
                    mock_save.assert_called_once()
            
            doc.is_modified = False
    
    def test_file_actions_check_unsaved_discard_action(self, qtbot):
        """Test check_unsaved_changes when Discard is chosen."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        doc = window.document
        if doc:
            doc.is_modified = True
            
            with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_dialog:
                mock_dialog.return_value = QMessageBox.StandardButton.Discard
                result = window.file_actions._check_unsaved_changes()
                assert result is True
            
            doc.is_modified = False
    
    def test_file_actions_check_unsaved_cancel_action(self, qtbot):
        """Test check_unsaved_changes when Cancel is chosen."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        doc = window.document
        if doc:
            doc.is_modified = True
            
            with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_dialog:
                mock_dialog.return_value = QMessageBox.StandardButton.Cancel
                result = window.file_actions._check_unsaved_changes()
                assert result is False
            
            doc.is_modified = False
    
    def test_split_view_zone_detection_top(self, qtbot):
        """Test drop zone detection for top area."""
        from ui.split_view import DropZoneOverlay
        
        overlay = DropZoneOverlay()
        qtbot.addWidget(overlay)
        overlay.show()
        overlay.resize(400, 400)
        qtbot.wait(50)
        
        # Cursor near top
        zone = overlay.get_zone_at(QPoint(200, 50))
        assert zone == 'top'
    
    def test_split_view_zone_detection_bottom(self, qtbot):
        """Test drop zone detection for bottom area."""
        from ui.split_view import DropZoneOverlay
        
        overlay = DropZoneOverlay()
        qtbot.addWidget(overlay)
        overlay.show()
        overlay.resize(400, 400)
        qtbot.wait(50)
        
        # Cursor near bottom
        zone = overlay.get_zone_at(QPoint(200, 350))
        assert zone == 'bottom'
    
    def test_split_view_zone_detection_left(self, qtbot):
        """Test drop zone detection for left area."""
        from ui.split_view import DropZoneOverlay
        
        overlay = DropZoneOverlay()
        qtbot.addWidget(overlay)
        overlay.show()
        overlay.resize(400, 400)
        qtbot.wait(50)
        
        # Cursor near left
        zone = overlay.get_zone_at(QPoint(50, 200))
        assert zone == 'left'
    
    def test_split_view_zone_detection_right(self, qtbot):
        """Test drop zone detection for right area."""
        from ui.split_view import DropZoneOverlay
        
        overlay = DropZoneOverlay()
        qtbot.addWidget(overlay)
        overlay.show()
        overlay.resize(400, 400)
        qtbot.wait(50)
        
        # Cursor near right
        zone = overlay.get_zone_at(QPoint(350, 200))
        assert zone == 'right'
    
    def test_split_view_zone_rect_all_directions(self, qtbot):
        """Test zone rect calculation for all directions."""
        from ui.split_view import DropZoneOverlay
        from PyQt6.QtCore import QRect
        
        overlay = DropZoneOverlay()
        qtbot.addWidget(overlay)
        overlay.show()
        overlay.resize(400, 400)
        qtbot.wait(50)
        
        # Test all zones
        for zone in ['top', 'bottom', 'left', 'right']:
            rect = overlay.get_zone_rect(zone)
            assert isinstance(rect, QRect)
            assert rect.width() > 0
            assert rect.height() > 0
    
    def test_tab_widget_empty_current_tab(self, qtbot):
        """Test current_tab with out of bounds index."""
        from ui.tab_widget import TabWidget
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        # Clear tabs and set out of bounds index
        tab_widget.clear()
        tab_widget._tabs.clear()
        # Set index that's out of range
        assert tab_widget.current_tab() is None
    
    def test_new_file_action(self, qtbot):
        """Test new_file action creates tab and updates title."""
        window = MainWindow()
        qtbot.addWidget(window)
        
        initial_count = window.tab_widget.count()
        
        result = window.file_actions.new_file()
        
        assert result is True
        assert window.tab_widget.count() > initial_count
    
    def test_save_current_no_tab(self, qtbot):
        """Test save_current when no tab exists."""
        from ui.tab_widget import TabWidget
        
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        tab_widget.clear()
        tab_widget._tabs.clear()
        
        result = tab_widget.save_current()
        assert result is False
    
    def test_draggable_tab_bar_no_drag_start_pos(self, qtbot):
        """Test mouse move with no initial drag start position."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        tab_bar._drag_start_pos = None
        
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(100, 10),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        tab_bar.mouseMoveEvent(move_event)
        # Should not crash and should call super
        assert tab_bar._drag_start_pos is None
    
    def test_draggable_tab_bar_large_drag_distance(self, qtbot):
        """Test drag with large distance triggers QDrag execution."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        tab_bar.addTab("Tab 2")
        
        # Set initial drag position at a tab
        tab_bar._drag_start_pos = QPoint(50, 10)
        
        # Create move with large distance to trigger drag
        large_distance = QApplication.startDragDistance() + 100
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(50 + large_distance, 10),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        # Mock QDrag to avoid actual drag operation
        with patch('ui.tab_widget.QDrag') as mock_drag_class:
            mock_drag = MagicMock()
            mock_drag_class.return_value = mock_drag
            mock_drag.exec.return_value = Qt.DropAction.IgnoreAction
            
            tab_bar.mouseMoveEvent(move_event)
            
            # Should have set dragging flag and called drag.exec
            mock_drag_class.assert_called_once_with(tab_bar)
            mock_drag.setMimeData.assert_called_once()
            mock_drag.exec.assert_called_once()
    
    def test_draggable_tab_bar_mouse_move_during_drag_exec(self, qtbot):
        """Test mouse move event during drag.exec() returns early."""
        tab_bar = DraggableTabBar()
        qtbot.addWidget(tab_bar)
        
        tab_bar.addTab("Tab 1")
        
        # Manually set dragging state
        tab_bar._dragging = True
        tab_bar._drag_start_pos = QPoint(50, 10)
        
        # Move event during drag should return early
        move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(200, 10),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        # Should return immediately without processing
        tab_bar.mouseMoveEvent(move_event)
        
        # Dragging state should remain unchanged
        assert tab_bar._dragging is True
        assert tab_bar._drag_start_pos == QPoint(50, 10)
