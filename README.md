# textedit-u0492257

## R1

### Opening and Saving Files
User can use the file system to create new files, open files, save files, or use save as. Clicking "open" or "new" prompts the user to save the current file if the file is currently not saved. However, there is no way to create, rename, or open files within the application's window as of now. The logic for this feature is handled in file_actions.py, and connected to the menu in menu_bar.py. These features were tested both by running the application and testing that documents were saved correctly and that the logic works as intended, and by running unit tests using pytests in test_file_acitons.py. 

### Keyboard Shortcuts
<img width="194" height="297" alt="Screenshot 2026-01-09 at 3 17 02 PM" src="https://github.com/user-attachments/assets/87668451-3ce8-49b5-8a22-900bc96ce806" />

Undo, Redo, Cut, Copy, Paste, and Select All were added as keyboard shortcuts, as well as to the edit menu. However, in the future I would like to add Ctrl+F to search for text, as well as other common shortcuts. These are handled in menu_bar.py. These shortcuts were all manually tested. 

### Editing and Selecting

This is handled by QPlainTextEdit from Qt, which allows the program to detect mouse movement, clicks, text input, etc. This feature was also manually tested.



