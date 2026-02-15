"""Extended tests for FileActions module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture
def mock_main_window():
    """Create a mock main window."""
    window = Mock()
    window.document = Mock()
    window.editor = Mock()
    window.tab_widget = Mock()
    return window


@pytest.fixture
def file_actions(mock_main_window):
    """Create FileActions with mock main window."""
    from actions.file_actions import FileActions
    return FileActions(mock_main_window)


class TestFileActionsProperties:
    """Test FileActions properties."""
    
    def test_tab_widget_property(self, file_actions, mock_main_window):
        """Test tab_widget property returns main window tab_widget."""
        assert file_actions.tab_widget == mock_main_window.tab_widget
    
    def test_editor_property(self, file_actions, mock_main_window):
        """Test editor property returns main window editor."""
        assert file_actions.editor == mock_main_window.editor
    
    def test_document_property(self, file_actions, mock_main_window):
        """Test document property returns main window document."""
        assert file_actions.document == mock_main_window.document


class TestGetDefaultDirectory:
    """Test get_default_directory function."""
    
    def test_get_default_directory_with_documents(self):
        """Test getting default directory when Documents exists."""
        from actions.file_actions import get_default_directory
        result = get_default_directory()
        assert isinstance(result, str)
        assert result != ""
    
    @patch('actions.file_actions.Path.home')
    def test_get_default_directory_no_documents(self, mock_home):
        """Test getting default directory when Documents doesn't exist."""
        from actions.file_actions import get_default_directory
        
        mock_path = Mock()
        mock_path.__truediv__ = Mock(return_value=Mock(exists=Mock(return_value=False)))
        mock_home.return_value = mock_path
        
        result = get_default_directory()
        assert isinstance(result, str)


class TestNewFile:
    """Test new_file method."""
    
    def test_new_file_success(self, file_actions, mock_main_window):
        """Test creating a new file."""
        mock_main_window.tab_widget.new_tab = Mock()
        mock_main_window.update_title = Mock()
        
        result = file_actions.new_file()
        
        assert result is True
        mock_main_window.tab_widget.new_tab.assert_called_once()
        mock_main_window.update_title.assert_called_once()


class TestCheckUnsavedChanges:
    """Test _check_unsaved_changes method."""
    
    def test_no_document(self, file_actions, mock_main_window):
        """Test when there's no document."""
        mock_main_window.document = None
        result = file_actions._check_unsaved_changes()
        assert result is True
    
    def test_document_not_modified(self, file_actions, mock_main_window):
        """Test when document is not modified."""
        mock_main_window.document.is_modified = False
        result = file_actions._check_unsaved_changes()
        assert result is True
    
    @patch('actions.file_actions.QMessageBox.question')
    def test_unsaved_changes_save(self, mock_question, file_actions, mock_main_window):
        """Test unsaved changes when user chooses Save."""
        mock_main_window.document.is_modified = True
        mock_main_window.document.display_name = "test.txt"
        mock_question.return_value = QMessageBox.StandardButton.Save
        file_actions.save_file = Mock(return_value=True)
        
        result = file_actions._check_unsaved_changes()
        
        assert result is True
        file_actions.save_file.assert_called_once()
    
    @patch('actions.file_actions.QMessageBox.question')
    def test_unsaved_changes_discard(self, mock_question, file_actions, mock_main_window):
        """Test unsaved changes when user chooses Discard."""
        mock_main_window.document.is_modified = True
        mock_main_window.document.display_name = "test.txt"
        mock_question.return_value = QMessageBox.StandardButton.Discard
        
        result = file_actions._check_unsaved_changes()
        
        assert result is True
    
    @patch('actions.file_actions.QMessageBox.question')
    def test_unsaved_changes_cancel(self, mock_question, file_actions, mock_main_window):
        """Test unsaved changes when user chooses Cancel."""
        mock_main_window.document.is_modified = True
        mock_main_window.document.display_name = "test.txt"
        mock_question.return_value = QMessageBox.StandardButton.Cancel
        
        result = file_actions._check_unsaved_changes()
        
        assert result is False


class TestOpenFile:
    """Test open_file method."""
    
    def test_open_file_with_path(self, file_actions, mock_main_window):
        """Test opening a file with explicit path."""
        mock_main_window.tab_widget.open_file = Mock(return_value=True)
        mock_main_window.update_title = Mock()
        
        result = file_actions.open_file("/path/to/file.txt")
        
        assert result is True
        mock_main_window.tab_widget.open_file.assert_called_once_with("/path/to/file.txt")
    
    def test_open_file_no_path_no_document(self, file_actions, mock_main_window):
        """Test opening file dialog when no document."""
        mock_main_window.document = None
        with patch('actions.file_actions.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.open_file()
            assert result is False
    
    def test_open_file_with_document_path(self, file_actions, mock_main_window):
        """Test opening file dialog starts in document directory."""
        mock_main_window.document.file_path = "/home/user/documents/file.txt"
        with patch('actions.file_actions.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.open_file()
            assert result is False
            # Verify it was called with the right start directory
            call_args = mock_dialog.call_args
            assert "/home/user/documents" in call_args[0][2]
    
    def test_open_file_dialog_cancelled(self, file_actions, mock_main_window):
        """Test when file dialog is cancelled."""
        mock_main_window.document = None
        with patch('actions.file_actions.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.open_file()
            assert result is False


class TestSaveFile:
    """Test save_file method."""
    
    def test_save_file_no_document(self, file_actions, mock_main_window):
        """Test saving when no document exists."""
        mock_main_window.document = None
        result = file_actions.save_file()
        assert result is False
    
    def test_save_file_untitled(self, file_actions, mock_main_window):
        """Test saving untitled file (calls save_file_as)."""
        mock_main_window.document.file_path = None
        file_actions.save_file_as = Mock(return_value=True)
        
        result = file_actions.save_file()
        
        assert result is True
        file_actions.save_file_as.assert_called_once()
    
    def test_save_file_existing(self, file_actions, mock_main_window):
        """Test saving existing file."""
        mock_main_window.document.file_path = "/path/to/file.txt"
        mock_main_window.tab_widget.save_current = Mock(return_value=True)
        mock_main_window.update_title = Mock()
        
        result = file_actions.save_file()
        
        assert result is True
        mock_main_window.tab_widget.save_current.assert_called_once()
        mock_main_window.update_title.assert_called_once()


class TestSaveFileAs:
    """Test save_file_as method."""
    
    def test_save_file_as_no_document(self, file_actions, mock_main_window):
        """Test save as when no document."""
        mock_main_window.document = None
        result = file_actions.save_file_as()
        assert result is False
    
    def test_save_file_as_no_editor(self, file_actions, mock_main_window):
        """Test save as when no editor."""
        mock_main_window.editor = None
        result = file_actions.save_file_as()
        assert result is False
    
    def test_save_file_as_dialog_cancelled(self, file_actions, mock_main_window):
        """Test when save dialog is cancelled."""
        with patch('actions.file_actions.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.save_file_as()
            assert result is False
    
    def test_save_file_as_success(self, file_actions, mock_main_window):
        """Test successful save as."""
        mock_main_window.document.file_path = "/old/path.txt"
        mock_main_window.editor.toPlainText = Mock(return_value="test content")
        mock_main_window.tab_widget.mark_current_saved = Mock()
        mock_main_window.update_title = Mock()
        
        with patch('actions.file_actions.QFileDialog.getSaveFileName') as mock_dialog:
            with patch('builtins.open') as mock_open:
                mock_dialog.return_value = ("/new/path.txt", "")
                mock_open.return_value.__enter__ = Mock()
                mock_open.return_value.__exit__ = Mock(return_value=False)
                
                result = file_actions.save_file_as()
                
                assert result is True
                mock_open.assert_called_once_with("/new/path.txt", "w", encoding="utf-8")
                mock_main_window.tab_widget.mark_current_saved.assert_called_once_with("/new/path.txt")
    
    def test_save_file_as_with_existing_path(self, file_actions, mock_main_window):
        """Test save as when document has existing path."""
        mock_main_window.document.file_path = "/old/path.txt"
        
        with patch('actions.file_actions.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.save_file_as()
            
            # Verify default path uses existing path
            call_args = mock_dialog.call_args
            assert "/old/path.txt" in call_args[0][2]
    
    def test_save_file_as_without_existing_path(self, file_actions, mock_main_window):
        """Test save as when document has no existing path."""
        mock_main_window.document.file_path = None
        mock_main_window.document.display_name = "Untitled"
        
        with patch('actions.file_actions.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ("", "")
            result = file_actions.save_file_as()
            
            # Verify default path uses display name
            call_args = mock_dialog.call_args
            assert "Untitled" in call_args[0][2]
    
    @patch('actions.file_actions.QMessageBox.critical')
    def test_save_file_as_write_error(self, mock_error, file_actions, mock_main_window):
        """Test save as when file write fails."""
        with patch('actions.file_actions.QFileDialog.getSaveFileName') as mock_dialog:
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                mock_dialog.return_value = ("/new/path.txt", "")
                
                result = file_actions.save_file_as()
                
                assert result is False
                mock_error.assert_called_once()
