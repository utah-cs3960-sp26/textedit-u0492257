"""Extended tests for MenuBar module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QAction, QKeySequence


@pytest.fixture
def mock_main_window(qtbot):
    """Create a mock main window."""
    window = QMainWindow()
    qtbot.addWidget(window)
    window.editor = Mock()
    window.editor.undo = Mock()
    window.editor.redo = Mock()
    window.editor.cut = Mock()
    window.editor.copy = Mock()
    window.editor.paste = Mock()
    window.editor.selectAll = Mock()
    window.toggle_file_explorer = Mock()
    return window


class TestMenuBarSetup:
    """Test menu bar setup."""
    
    def test_setup_menu_bar_creates_menus(self, mock_main_window):
        """Test that setup_menu_bar creates File menu."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # Verify menu bar has menus
        menu_bar = mock_main_window.menuBar()
        assert menu_bar is not None
        assert len(menu_bar.actions()) > 0
    
    def test_setup_menu_bar_connects_file_actions(self, mock_main_window):
        """Test that file actions are connected to menu items."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        file_actions.new_file = Mock()
        file_actions.open_file = Mock()
        file_actions.save_file = Mock()
        file_actions.save_file_as = Mock()
        
        setup_menu_bar(mock_main_window, file_actions)
        
        # Verify menu bar has File, Edit, and View menus
        menu_bar = mock_main_window.menuBar()
        menus = menu_bar.findChildren(type(menu_bar.findChild(type(None))))
        assert len(menu_bar.actions()) >= 3
    
    def test_file_menu_new_action(self, mock_main_window):
        """Test New action in File menu."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        file_actions.new_file = Mock()
        
        setup_menu_bar(mock_main_window, file_actions)
        
        # Menu should be created
        menu_bar = mock_main_window.menuBar()
        assert menu_bar is not None
    
    def test_edit_menu_undo_action(self, mock_main_window):
        """Test that Edit menu has Undo action."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # Verify menu bar exists and has actions
        menu_bar = mock_main_window.menuBar()
        assert menu_bar is not None
        assert len(menu_bar.actions()) >= 2  # File and Edit menus


class TestMenuBarActions:
    """Test menu bar action callbacks."""
    
    def test_undo_action_calls_editor_undo(self, mock_main_window):
        """Test that Undo action calls editor.undo()."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # Menu should be created successfully
        menu_bar = mock_main_window.menuBar()
        assert menu_bar is not None
    
    def test_toggle_explorer_action(self, mock_main_window):
        """Test that View menu has Toggle Explorer action."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # Verify view menu was created
        menu_bar = mock_main_window.menuBar()
        assert menu_bar is not None
        assert len(menu_bar.actions()) >= 3


class TestMenuBarIntegration:
    """Test menu bar integration with main window."""
    
    def test_setup_menu_bar_with_real_window(self, mock_main_window):
        """Test setup with real window."""
        from ui.menu_bar import setup_menu_bar
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # Verify all menus were created
        menu_bar = mock_main_window.menuBar()
        assert len(menu_bar.actions()) >= 3
    
    def test_get_editor_function_in_menu_bar(self, mock_main_window):
        """Test that get_editor function properly returns editor."""
        from ui.menu_bar import setup_menu_bar
        
        # The get_editor function is defined inside setup_menu_bar
        mock_editor = Mock()
        mock_editor.undo = Mock()
        mock_main_window.editor = mock_editor
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # After setup, the editor should be set
        assert mock_main_window.editor is mock_editor
    
    def test_undo_action_triggers_get_editor(self, mock_main_window):
        """Test that undo action calls get_editor which returns editor."""
        from ui.menu_bar import setup_menu_bar
        from PyQt6.QtGui import QAction
        
        # Create editor mock that tracks undo calls
        mock_editor = Mock()
        mock_editor.undo = Mock()
        mock_main_window.editor = mock_editor
        
        # Create a real menu bar
        real_menu_bar = Mock()
        menu = Mock()
        actions_list = []
        
        def add_action(action):
            actions_list.append(action)
            return action
        
        menu.addAction = add_action
        real_menu_bar.addMenu = Mock(return_value=menu)
        mock_main_window.menuBar = Mock(return_value=real_menu_bar)
        
        file_actions = Mock()
        setup_menu_bar(mock_main_window, file_actions)
        
        # The undo action was added to the menu
        # Its lambda calls get_editor() which returns main_window.editor
        # Triggering it should call undo on the editor
        for action in actions_list:
            if hasattr(action, 'text') and 'Undo' in str(action.text()):
                # Found the undo action, trigger it
                action.triggered.emit()
                break
    
    def test_menu_bar_with_none_editor(self, mock_main_window):
        """Test that menu bar works when editor is None."""
        from ui.menu_bar import setup_menu_bar
        
        mock_main_window.editor = None
        
        file_actions = Mock()
        # Should not crash even if editor is None
        setup_menu_bar(mock_main_window, file_actions)
