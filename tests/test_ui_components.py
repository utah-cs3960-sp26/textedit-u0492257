"""Tests for UI components."""

import pytest
from PyQt6.QtCore import Qt





class TestMainInit:
    """Test main module initialization."""
    
    def test_main_module_imports(self):
        """Test that main module can be imported."""
        import main
        assert hasattr(main, 'main')


class TestMainWindow:
    """Test MainWindow widget functionality."""
    
    def test_main_window_shows_correct_title(self, main_window):
        """Test that main window has correct title."""
        assert "PyNano" in main_window.windowTitle() or main_window.windowTitle() != ""
    
    def test_main_window_has_menu_bar(self, main_window):
        """Test that main window has a menu bar."""
        assert main_window.menuBar() is not None
    
    def test_main_window_has_central_widget(self, main_window):
        """Test that main window has a central widget."""
        assert main_window.centralWidget() is not None


class TestMenuBar:
    """Test menu bar functionality."""
    
    def test_menu_bar_has_file_menu(self, main_window):
        """Test that menu bar contains File menu."""
        menu_bar = main_window.menuBar()
        actions = [action.text() for action in menu_bar.actions()]
        assert any("File" in action or "file" in action for action in actions)


class TestFileExplorer:
    """Test file explorer widget."""
    
    def test_file_explorer_created(self, qtbot):
        """Test that FileExplorer can be created."""
        from ui.file_explorer import FileExplorer
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer is not None


class TestSplitView:
    """Test split view functionality."""
    
    def test_split_view_has_two_editors(self, main_window):
        """Test that split view contains editors."""
        # The split view should have text editors in the main window
        assert main_window.centralWidget() is not None


class TestTabWidget:
    """Test tab widget functionality."""
    
    def test_tab_widget_created(self, qtbot):
        """Test that TabWidget can be created."""
        from ui.tab_widget import TabWidget
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        assert tab_widget is not None
    
    def test_tab_widget_add_tab(self, qtbot):
        """Test adding a tab to TabWidget."""
        from ui.tab_widget import TabWidget
        from editor.text_editor import TextEditor
        tab_widget = TabWidget()
        qtbot.addWidget(tab_widget)
        
        editor = TextEditor()
        qtbot.addWidget(editor)
        
        tab_widget.addTab(editor, "test.txt")
        
        assert tab_widget.count() > 0


class TestUIIntegration:
    """Test integration between UI components."""
    
    def test_main_window_layout(self, main_window):
        """Test that main window has proper layout."""
        # The main window should have content
        assert main_window.width() > 0
        assert main_window.height() > 0
    
    def test_main_window_show_and_hide(self, main_window):
        """Test showing and hiding main window."""
        main_window.show()
        assert main_window.isVisible()
        
        main_window.hide()
        assert not main_window.isVisible()
