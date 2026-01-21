"""Main application window."""

from PyQt6.QtWidgets import QMainWindow, QSplitter
from PyQt6.QtCore import Qt

from actions.file_actions import FileActions
from ui.menu_bar import setup_menu_bar
from ui.file_explorer import FileExplorer
from ui.split_view import SplitViewManager


class MainWindow(QMainWindow):
    """Main window with vintage terminal styling."""
    
    def __init__(self):
        super().__init__()
        
        # Create split view manager and file explorer
        self.split_view_manager = SplitViewManager()
        self.split_view_manager.tab_widget.current_document_changed.connect(self.update_title)
        self.file_explorer = FileExplorer(self)
        self.file_actions = FileActions(self)
        
        self._setup_ui()
        self._connect_signals()
    
    @property
    def tab_widget(self):
        """Get the primary tab widget (for compatibility)."""
        return self.split_view_manager.tab_widget
    
    def _setup_ui(self):
        """Initialize the user interface."""
        # Create splitter for file explorer and split view manager
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.file_explorer)
        self.splitter.addWidget(self.split_view_manager)
        
        # Set initial sizes (200px for explorer, rest for editor)
        self.splitter.setSizes([200, 600])
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(1, False)
        
        self.setCentralWidget(self.splitter)
        self.resize(1000, 600)
        
        self.actions = setup_menu_bar(self, self.file_actions)
        self.update_title()
    
    def _connect_signals(self):
        """Connect signals to update window state."""
        self.file_explorer.file_selected.connect(self._on_file_selected)
    
    def _on_file_selected(self, file_path):
        """Open file selected from file explorer in a new tab."""
        self.tab_widget.new_tab(file_path)
    
    @property
    def editor(self):
        """Get the current editor (for compatibility)."""
        return self.split_view_manager.current_editor
    
    @property
    def document(self):
        """Get the current document (for compatibility)."""
        return self.split_view_manager.current_document
    
    def toggle_file_explorer(self):
        """Toggle visibility of the file explorer."""
        if self.file_explorer.isVisible():
            self._explorer_width = self.splitter.sizes()[0]
            self.file_explorer.hide()
        else:
            self.file_explorer.show()
            width = getattr(self, '_explorer_width', 200)
            self.splitter.setSizes([width, self.splitter.sizes()[1]])
    
    def update_title(self):
        """Update window title with filename and modified indicator."""
        doc = self.document
        if doc:
            title = f"PyNano - {doc.display_name}"
            if doc.is_modified:
                title += " *"
        else:
            title = "PyNano"
        self.setWindowTitle(title)
    
    def closeEvent(self, event):
        """Handle window close with unsaved changes check."""
        if self.file_actions._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()
