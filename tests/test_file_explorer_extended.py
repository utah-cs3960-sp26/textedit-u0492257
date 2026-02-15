"""Extended tests for FileExplorer to achieve 100% coverage."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication

from ui.file_explorer import FileExplorer


class TestFileExplorerInit:
    """Test FileExplorer initialization."""
    
    def test_file_explorer_init(self, qtbot):
        """Test FileExplorer can be initialized."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer is not None
        assert explorer._root_path is None
    
    def test_file_explorer_with_parent(self, qtbot):
        """Test FileExplorer with parent widget."""
        from PyQt6.QtWidgets import QWidget
        parent = QWidget()
        qtbot.addWidget(parent)
        explorer = FileExplorer(parent=parent)
        qtbot.addWidget(explorer)
        assert explorer.parent() == parent


class TestFileExplorerUI:
    """Test FileExplorer UI components."""
    
    def test_has_open_file_button(self, qtbot):
        """Test that open file button exists."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert hasattr(explorer, 'open_file_btn')
        assert explorer.open_file_btn is not None
    
    def test_has_open_folder_button(self, qtbot):
        """Test that open folder button exists."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert hasattr(explorer, 'open_folder_btn')
        assert explorer.open_folder_btn is not None
    
    def test_has_tree_view(self, qtbot):
        """Test that tree view exists."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert hasattr(explorer, 'tree')
        assert explorer.tree is not None
    
    def test_has_stacked_widget(self, qtbot):
        """Test that stacked widget exists."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert hasattr(explorer, 'stack')
        assert explorer.stack is not None
    
    def test_has_folder_label(self, qtbot):
        """Test that folder label exists."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert hasattr(explorer, 'folder_label')
        assert explorer.folder_label is not None
    
    def test_initial_stack_index_is_empty_state(self, qtbot):
        """Test that initial stack shows empty state."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.stack.currentIndex() == 0
    
    def test_folder_label_initially_hidden(self, qtbot):
        """Test that folder label is initially hidden."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert not explorer.folder_label.isVisible()


class TestFileExplorerSetRootPath:
    """Test FileExplorer set_root_path functionality."""
    
    def test_set_root_path_with_valid_directory(self, qtbot):
        """Test setting root path with a valid directory."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            assert explorer._root_path == tmpdir
            assert explorer.stack.currentIndex() == 1
    
    def test_set_root_path_shows_folder_label(self, qtbot):
        """Test that folder label is shown after setting root path."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        explorer.show()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            qtbot.wait(50)  # Process events
            assert explorer.folder_label.isVisible()
    
    def test_set_root_path_updates_folder_label_text(self, qtbot):
        """Test that folder label shows folder name."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_name = Path(tmpdir).name
            explorer.set_root_path(tmpdir)
            assert folder_name in explorer.folder_label.text()
    
    def test_set_root_path_emits_signal(self, qtbot):
        """Test that set_root_path emits folder_opened signal."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with qtbot.waitSignal(explorer.folder_opened):
            with tempfile.TemporaryDirectory() as tmpdir:
                explorer.set_root_path(tmpdir)
    
    def test_set_root_path_sets_model_root(self, qtbot):
        """Test that model root is set correctly."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            # Verify the model has the correct root path
            assert explorer.model.rootPath() == tmpdir


class TestFileExplorerCloseFolder:
    """Test FileExplorer close_folder functionality."""
    
    def test_close_folder_resets_root_path(self, qtbot):
        """Test that close_folder resets root path."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            explorer.close_folder()
            assert explorer._root_path is None
    
    def test_close_folder_hides_folder_label(self, qtbot):
        """Test that close_folder hides folder label."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            explorer.close_folder()
            assert not explorer.folder_label.isVisible()
    
    def test_close_folder_returns_to_empty_state(self, qtbot):
        """Test that close_folder returns to empty state."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            explorer.close_folder()
            assert explorer.stack.currentIndex() == 0


class TestFileExplorerRootPath:
    """Test FileExplorer root_path getter."""
    
    def test_root_path_getter_returns_none_initially(self, qtbot):
        """Test that root_path returns None initially."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.root_path() is None
    
    def test_root_path_getter_returns_set_path(self, qtbot):
        """Test that root_path returns the set path."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            assert explorer.root_path() == tmpdir
    
    def test_root_path_getter_returns_none_after_close(self, qtbot):
        """Test that root_path returns None after closing folder."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            explorer.set_root_path(tmpdir)
            explorer.close_folder()
            assert explorer.root_path() is None


class TestFileExplorerOpenFileDialog:
    """Test FileExplorer open file dialog."""
    
    def test_open_file_dialog_cancelled(self, qtbot):
        """Test opening file dialog and cancelling."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with patch('ui.file_explorer.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            explorer._open_file_dialog()
            # Should not emit signal or change state
            assert explorer._root_path is None
    
    def test_open_file_dialog_with_valid_file(self, qtbot):
        """Test opening file dialog with valid file."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            
            with patch('ui.file_explorer.QFileDialog.getOpenFileName') as mock_dialog:
                mock_dialog.return_value = (str(test_file), "")
                
                with qtbot.waitSignals([explorer.file_selected, explorer.folder_opened]):
                    explorer._open_file_dialog()
                
                assert explorer._root_path == tmpdir
    
    def test_open_file_dialog_emits_file_selected_signal(self, qtbot):
        """Test that file selection emits file_selected signal."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            
            with patch('ui.file_explorer.QFileDialog.getOpenFileName') as mock_dialog:
                mock_dialog.return_value = (str(test_file), "")
                
                with qtbot.waitSignal(explorer.file_selected):
                    explorer._open_file_dialog()


class TestFileExplorerOpenFolderDialog:
    """Test FileExplorer open folder dialog."""
    
    def test_open_folder_dialog_cancelled(self, qtbot):
        """Test opening folder dialog and cancelling."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with patch('ui.file_explorer.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = ""
            explorer._open_folder_dialog()
            # Should not change state
            assert explorer._root_path is None
    
    def test_open_folder_dialog_with_valid_folder(self, qtbot):
        """Test opening folder dialog with valid folder."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('ui.file_explorer.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = tmpdir
                
                with qtbot.waitSignal(explorer.folder_opened):
                    explorer._open_folder_dialog()
                
                assert explorer._root_path == tmpdir
    
    def test_open_folder_dialog_switches_to_tree_view(self, qtbot):
        """Test that folder selection switches to tree view."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('ui.file_explorer.QFileDialog.getExistingDirectory') as mock_dialog:
                mock_dialog.return_value = tmpdir
                explorer._open_folder_dialog()
                assert explorer.stack.currentIndex() == 1


class TestFileExplorerTreeInteraction:
    """Test FileExplorer tree view interactions."""
    
    def test_tree_double_click_on_file(self, qtbot):
        """Test double-clicking on a file in tree."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            explorer.set_root_path(tmpdir)
            
            # Get the index of the file in the tree
            file_index = explorer.model.index(str(test_file))
            
            with qtbot.waitSignal(explorer.file_selected):
                explorer._on_item_double_clicked(file_index)
    
    def test_tree_double_click_on_directory(self, qtbot):
        """Test double-clicking on a directory in tree."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            
            explorer.set_root_path(tmpdir)
            
            # Get the index of the directory in the tree
            dir_index = explorer.model.index(str(subdir))
            
            # Double-click on directory should not emit file_selected signal
            # since it's not a file
            with patch.object(explorer, 'file_selected') as mock_signal:
                explorer._on_item_double_clicked(dir_index)
                # Signal should not be emitted for directories
                mock_signal.emit.assert_not_called()


class TestFileExplorerButtonConnections:
    """Test FileExplorer button connections."""
    
    def test_open_file_button_connection(self, qtbot):
        """Test that open file button is connected."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with patch('ui.file_explorer.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            qtbot.mouseClick(explorer.open_file_btn, Qt.MouseButton.LeftButton)
            qtbot.wait(50)  # Allow event to process
            mock_dialog.assert_called_once()
    
    def test_open_folder_button_connection(self, qtbot):
        """Test that open folder button is connected."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        
        with patch('ui.file_explorer.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = ""
            qtbot.mouseClick(explorer.open_folder_btn, Qt.MouseButton.LeftButton)
            qtbot.wait(50)  # Allow event to process
            mock_dialog.assert_called_once()


class TestFileExplorerTreeProperties:
    """Test FileExplorer tree view properties."""
    
    def test_tree_is_animated(self, qtbot):
        """Test that tree view is animated."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.tree.isAnimated()
    
    def test_tree_has_indentation(self, qtbot):
        """Test that tree has indentation."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.tree.indentation() == 16
    
    def test_tree_sorting_enabled(self, qtbot):
        """Test that tree sorting is enabled."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.tree.isSortingEnabled()
    
    def test_tree_header_hidden(self, qtbot):
        """Test that tree header is hidden."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert explorer.tree.isHeaderHidden()
    
    def test_tree_columns_hidden(self, qtbot):
        """Test that non-name columns are hidden."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        for i in range(1, 4):
            assert explorer.tree.isColumnHidden(i)
    
    def test_tree_name_column_visible(self, qtbot):
        """Test that name column is visible."""
        explorer = FileExplorer()
        qtbot.addWidget(explorer)
        assert not explorer.tree.isColumnHidden(0)
