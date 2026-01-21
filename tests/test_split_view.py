"""Tests for split view functionality."""

import pytest
from PyQt6.QtCore import QSize


@pytest.fixture
def split_view_manager(qtbot):
    """Create a SplitViewManager instance."""
    from ui.split_view import SplitViewManager
    manager = SplitViewManager()
    qtbot.addWidget(manager)
    return manager


class TestSplitViewManager:
    """Tests for SplitViewManager."""
    
    def test_initial_state_not_split(self, split_view_manager):
        """Manager starts with no splits."""
        assert not split_view_manager.is_split
        assert split_view_manager.split_count() == 1
        assert split_view_manager.original_size is None
    
    def test_store_original_size(self, split_view_manager):
        """Original size is stored correctly."""
        size = QSize(1000, 600)
        split_view_manager.store_original_size(size)
        assert split_view_manager.original_size == size
    
    def test_store_original_size_only_once(self, split_view_manager):
        """Original size is only stored once."""
        size1 = QSize(1000, 600)
        size2 = QSize(1200, 800)
        split_view_manager.store_original_size(size1)
        split_view_manager.store_original_size(size2)
        assert split_view_manager.original_size == size1
    
    def test_split_creates_new_pane(self, split_view_manager, tmp_path):
        """Splitting creates a new pane."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        initial_count = split_view_manager.split_count()
        pane = split_view_manager._panes[0]
        split_view_manager._handle_split(pane, 'right', str(test_file))
        
        assert split_view_manager.split_count() == initial_count + 1
        assert split_view_manager.is_split
    
    def test_close_pane_reduces_count(self, split_view_manager, tmp_path):
        """Closing a pane reduces the count."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        pane = split_view_manager._panes[0]
        split_view_manager._handle_split(pane, 'right', str(test_file))
        
        assert split_view_manager.split_count() == 2
        
        new_pane = split_view_manager._panes[1]
        split_view_manager.close_pane(new_pane)
        
        assert split_view_manager.split_count() == 1
        assert not split_view_manager.is_split
    
    def test_cannot_close_last_pane(self, split_view_manager):
        """Cannot close the last remaining pane."""
        pane = split_view_manager._panes[0]
        result = split_view_manager.close_pane(pane)
        
        assert result is False
        assert split_view_manager.split_count() == 1
    
    def test_close_all_splits(self, split_view_manager, tmp_path):
        """close_all_splits removes all split panes."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        pane = split_view_manager._panes[0]
        split_view_manager._handle_split(pane, 'right', str(test_file))
        split_view_manager._handle_split(pane, 'bottom', str(test_file))
        
        assert split_view_manager.split_count() == 3
        
        split_view_manager.close_all_splits()
        
        assert split_view_manager.split_count() == 1
        assert not split_view_manager.is_split


class TestSplitViewWindowSize:
    """Tests for window size restoration after closing splits."""
    
    def test_closing_split_reverts_to_original_size(self, main_window, tmp_path, qtbot):
        """Closing last split reverts window to original size."""
        original_size = QSize(1000, 600)
        main_window.resize(original_size)
        qtbot.waitExposed(main_window)
        main_window.show()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        manager._handle_split(pane, 'right', str(test_file))
        
        assert manager.is_split
        assert manager.original_size == original_size
        
        new_pane = manager._panes[1]
        manager.close_pane(new_pane)
        
        assert not manager.is_split
        assert manager.original_size is None
        assert main_window.size() == original_size
    
    def test_original_size_restored_after_multiple_splits(self, main_window, tmp_path, qtbot):
        """Original size is restored even after multiple splits."""
        original_size = QSize(1000, 600)
        main_window.resize(original_size)
        qtbot.waitExposed(main_window)
        main_window.show()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        manager._handle_split(pane, 'right', str(test_file))
        manager._handle_split(pane, 'bottom', str(test_file))
        
        assert manager.split_count() == 3
        stored_size = manager.original_size
        assert stored_size == original_size
        
        manager.close_all_splits()
        
        assert main_window.size() == original_size
    
    def test_split_stores_size_before_first_split_only(self, main_window, tmp_path, qtbot):
        """Size is stored only before the first split, not subsequent ones."""
        original_size = QSize(1000, 600)
        main_window.resize(original_size)
        qtbot.waitExposed(main_window)
        main_window.show()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        manager._handle_split(pane, 'right', str(test_file))
        stored_after_first = manager.original_size
        
        main_window.resize(QSize(1200, 800))
        
        manager._handle_split(pane, 'bottom', str(test_file))
        stored_after_second = manager.original_size
        
        assert stored_after_first == original_size
        assert stored_after_second == original_size


class TestClosingLastTabClosesSplitPane:
    """Tests for closing last tab in split pane."""
    
    def test_closing_last_tab_closes_split_pane(self, split_view_manager, tmp_path):
        """Closing the last tab in a split pane closes that pane."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        pane = split_view_manager._panes[0]
        split_view_manager._handle_split(pane, 'right', str(test_file))
        
        assert split_view_manager.split_count() == 2
        assert split_view_manager.is_split
        
        new_pane = split_view_manager._panes[1]
        tab = new_pane.tab_widget.current_tab()
        new_pane.tab_widget._close_tab(tab)
        
        assert split_view_manager.split_count() == 1
        assert not split_view_manager.is_split
    
    def test_closing_last_tab_restores_original_size(self, main_window, tmp_path, qtbot):
        """Closing last tab in split pane restores original window size."""
        original_size = QSize(1000, 600)
        main_window.resize(original_size)
        qtbot.waitExposed(main_window)
        main_window.show()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        manager._handle_split(pane, 'right', str(test_file))
        
        assert manager.is_split
        
        new_pane = manager._panes[1]
        tab = new_pane.tab_widget.current_tab()
        new_pane.tab_widget._close_tab(tab)
        
        assert not manager.is_split
        assert main_window.size() == original_size


class TestEqualSplitSizes:
    """Tests for equal split pane sizes."""
    
    def test_horizontal_split_creates_equal_widths(self, main_window, tmp_path, qtbot):
        """Splitting left/right creates panes of equal width."""
        main_window.resize(1000, 600)
        main_window.show()
        qtbot.waitExposed(main_window)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        initial_width = pane.width()
        
        manager._handle_split(pane, 'right', str(test_file))
        
        qtbot.wait(50)
        
        pane1_width = manager._panes[0].width()
        pane2_width = manager._panes[1].width()
        
        assert abs(pane1_width - pane2_width) <= 5
    
    def test_vertical_split_creates_equal_heights(self, main_window, tmp_path, qtbot):
        """Splitting top/bottom creates panes of equal height."""
        main_window.resize(1000, 600)
        main_window.show()
        qtbot.waitExposed(main_window)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        initial_height = pane.height()
        
        manager._handle_split(pane, 'bottom', str(test_file))
        
        qtbot.wait(50)
        
        pane1_height = manager._panes[0].height()
        pane2_height = manager._panes[1].height()
        
        assert abs(pane1_height - pane2_height) <= 5
    
    def test_tab_drag_horizontal_split_equal_widths(self, main_window, tmp_path, qtbot):
        """Dragging tab left/right creates panes of equal width."""
        main_window.resize(1000, 600)
        main_window.show()
        qtbot.waitExposed(main_window)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        manager._handle_split(pane, 'right', str(test_file))
        
        qtbot.wait(50)
        
        pane1_width = manager._panes[0].width()
        pane2_width = manager._panes[1].width()
        
        assert abs(pane1_width - pane2_width) <= 5
    
    def test_tab_drag_vertical_split_equal_heights(self, main_window, tmp_path, qtbot):
        """Dragging tab top/bottom creates panes of equal height."""
        main_window.resize(1000, 600)
        main_window.show()
        qtbot.waitExposed(main_window)
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager = main_window.split_view_manager
        pane = manager._panes[0]
        
        manager._handle_split(pane, 'bottom', str(test_file))
        
        qtbot.wait(50)
        
        pane1_height = manager._panes[0].height()
        pane2_height = manager._panes[1].height()
        
        assert abs(pane1_height - pane2_height) <= 5


class TestDropZones:
    """Tests for drop zone detection."""
    
    def test_top_zone_detection(self, split_view_manager):
        """Top zone is detected when cursor is closest to top edge."""
        from PyQt6.QtCore import QPoint
        
        pane = split_view_manager._panes[0]
        pane.resize(400, 400)
        overlay = pane.drop_overlay
        overlay.setGeometry(pane.rect())
        
        top_point = QPoint(200, 50)
        assert overlay.get_zone_at(top_point) == 'top'
    
    def test_bottom_zone_detection(self, split_view_manager):
        """Bottom zone is detected when cursor is closest to bottom edge."""
        from PyQt6.QtCore import QPoint
        
        pane = split_view_manager._panes[0]
        pane.resize(400, 400)
        overlay = pane.drop_overlay
        overlay.setGeometry(pane.rect())
        
        bottom_point = QPoint(200, 350)
        assert overlay.get_zone_at(bottom_point) == 'bottom'
    
    def test_left_zone_detection(self, split_view_manager):
        """Left zone is detected when cursor is closest to left edge."""
        from PyQt6.QtCore import QPoint
        
        pane = split_view_manager._panes[0]
        pane.resize(400, 400)
        overlay = pane.drop_overlay
        overlay.setGeometry(pane.rect())
        
        left_point = QPoint(50, 200)
        assert overlay.get_zone_at(left_point) == 'left'
    
    def test_right_zone_detection(self, split_view_manager):
        """Right zone is detected when cursor is closest to right edge."""
        from PyQt6.QtCore import QPoint
        
        pane = split_view_manager._panes[0]
        pane.resize(400, 400)
        overlay = pane.drop_overlay
        overlay.setGeometry(pane.rect())
        
        right_point = QPoint(350, 200)
        assert overlay.get_zone_at(right_point) == 'right'
    
    def test_zone_rect_covers_half(self, split_view_manager):
        """Zone rectangles cover half the window."""
        pane = split_view_manager._panes[0]
        pane.resize(400, 400)
        overlay = pane.drop_overlay
        overlay.setGeometry(pane.rect())
        
        top_rect = overlay.get_zone_rect('top')
        assert top_rect.height() == 200
        assert top_rect.width() == 400
        
        left_rect = overlay.get_zone_rect('left')
        assert left_rect.width() == 200
        assert left_rect.height() == 400
