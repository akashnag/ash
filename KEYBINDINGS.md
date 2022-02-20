# Key Bindings for ash

The following is a list of default key bindings for **ash**. All of these can be remapped as per the user's preferences by creating new keymaps in the `~/.ash-editor/keymaps/` directory. The default keymap is stored in the file 'default.json'.

### Global key combinations

These key combinations can be used even if no editor is currently active.

| Key | Action |
|-----|--------|
|<kbd>Ctrl</kbd> + <kbd>Q</kbd>|Close the active window|
|<kbd>Ctrl</kbd> + <kbd>@</kbd>|Forcefully quit the application, discarding all changes|
|<kbd>Tab</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>I</kbd>|Switch focus to the next widget in the active dialog-box (if any)|
|<kbd>Shift</kbd> + <kbd>Tab</kbd>|Switch focus to the previous widget in the active dialog-box|
|<kbd>Ctrl</kbd> + <kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Move the active dialog-box around the screen|
|<kbd>Space</kbd>|Check/Uncheck a checkbox in focus|
|<kbd>Enter</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>W</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>J</kbd>|Save changes and close the current dialog box|
|<kbd>Alt</kbd> + <kbd>&#8595;</kbd>|Open the top-level menu|
|<kbd>Alt</kbd> + <kbd>&#8593;</kbd>|Close/hide the top-level menu|
|<kbd>Ctrl</kbd> + <kbd>L</kbd>|Show the list of active buffers/files|
|<kbd>Ctrl</kbd> + <kbd>T</kbd>|Show the list of active tabs|
|<kbd>Ctrl</kbd> + <kbd>N</kbd>|Open a new buffer for editing|
|<kbd>Ctrl</kbd> + <kbd>O</kbd>|Open a file|
|<kbd>Ctrl</kbd> + <kbd>E</kbd>|Open project explorer (if directory has been opened)|
|<kbd>F1</kbd>|Show Help|
|<kbd>F2</kbd>|Show the list of recently opened files|
|<kbd>F3</kbd>|Switch to previous editor|
|<kbd>F4</kbd>|Switch to next editor|
|<kbd>F5</kbd>|Switch to previous tab|
|<kbd>F6</kbd>|Switch to next tab|
|<kbd>F11</kbd>|Toggle fullscreen|
|<kbd>Ctrl</kbd> + <kbd>F1</kbd>|Shows/hides filenames in non-active editors|
|<kbd>Ctrl</kbd> + <kbd>F2</kbd>|Create a new tab|
|<kbd>Ctrl</kbd> + <kbd>F3</kbd>|Split horizontally|
|<kbd>Ctrl</kbd> + <kbd>F4</kbd>|Split vertically|
|<kbd>Ctrl</kbd> + <kbd>F5</kbd>|Merge horizontally|
|<kbd>Ctrl</kbd> + <kbd>F6</kbd>|Merge vertically|
|<kbd>Ctrl</kbd> + <kbd>F7</kbd>|Close the active tab|
|<kbd>Ctrl</kbd> + <kbd>F9</kbd>|Close all editors in the active-tab except the active-editor|
|<kbd>Esc</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>[</kbd>|Show the command window|
|<kbd>F12</kbd>|Search in all open files/buffers|
|<kbd>Ctrl</kbd> + <kbd>F12</kbd>|Search/Replace in all open files/buffers|

Apart from the above, selection and cursor-movement using <kbd>Shift</kbd> and/or arrow / <kbd>Home</kbd> / <kbd>End</kbd> keys, as well as Cut / Copy / Paste (using <kbd>Ctrl</kbd> + <kbd>X</kbd> / <kbd>C</kbd> / <kbd>V</kbd> respectively) work in all text-fields (wherever they occur in dialog-boxes).

### Editor commands

These key combinations work only if an editor is currently active.

| Key | Action |
|-----|--------|
|<kbd>Alt</kbd> + <kbd>&#8594;</kbd> _or_ Right-Click|Open popup menu|
|<kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Move the cursor in the document one character/line at a time|
|<kbd>Ctrl</kbd> + <kbd>&#8592;</kbd> <kbd>&#8594;</kbd>|Move the cursor one word at a time|
|<kbd>PgUp</kbd> <kbd>PgDown</kbd>|Move the cursor in the document one screenful at a time|
|<kbd>Home</kbd> <kbd>End</kbd>|Move the cursor to the beginning/end of the current line|
|<kbd>Ctrl</kbd> + <kbd>Home</kbd> <kbd>End</kbd>|Move the cursor to the beginning/end of the current document|
|<kbd>Tab</kbd>|Insert tab OR Increase the indent of the selection|
|<kbd>Shift</kbd> + <kbd>Tab</kbd>|Decrease the indent of the selection if possible|
|<kbd>Shift</kbd> + <kbd>Home</kbd> <kbd>End</kbd>|Select text up to the beginning/end of the current line|
|<kbd>Shift</kbd> + <kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Select text one character at a time|
|<kbd>Shift</kbd> + <kbd>PgUp</kbd> <kbd>PgDown</kbd>|Select one screenful at a time|
|<kbd>Ctrl</kbd> + <kbd>A</kbd>|Select all|
|<kbd>Ctrl</kbd> + <kbd>C</kbd>|Copy|
|<kbd>Ctrl</kbd> + <kbd>X</kbd>|Cut|
|<kbd>Ctrl</kbd> + <kbd>V</kbd>|Paste|
|<kbd>Backspace</kbd>|Delete the character/selected-text before the cursor|
|<kbd>Del</kbd>|Delete the selected-text or, character at the cursor position|
|<kbd>Ctrl</kbd> + <kbd>F2</kbd>|Convert all Uncode escape sequences (\uxxxx) to Unicode characters, and also sets file encoding to UTF-8|
|<kbd>Ctrl</kbd> + <kbd>S</kbd>|Save the current file/buffer|
|<kbd>Ctrl</kbd> + <kbd>W</kbd>|Save the current buffer/file and close the editor|
|<kbd>F9</kbd>|Save As...|
|<kbd>Ctrl</kbd> + <kbd>P</kbd>|Open the preferences dialog-box|
|<kbd>Ctrl</kbd> + <kbd>G</kbd>|Go to a given line/column|
|<kbd>Ctrl</kbd> + <kbd>Z</kbd>|Undo|
|<kbd>Ctrl</kbd> + <kbd>Y</kbd>|Redo|
|<kbd>Ctrl</kbd> + <kbd>F</kbd>|Find|
|<kbd>Ctrl</kbd> + <kbd>H</kbd>|Replace|
|<kbd>Ctrl</kbd> + <kbd>K</kbd>|Add a cursor below|
|<kbd>Ctrl</kbd> + <kbd>^</kbd>|Cancel multi-cursor mode|

### Commands for find and replace operations

These key combinations work when the Find/Replace dialog box is active:

| Key | Action |
|-----|--------|
|<kbd>Enter</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>J</kbd>|Find next match|
|<kbd>F7</kbd>|Find previous match|
|<kbd>F8</kbd>|Replace the current match|
|<kbd>Ctrl</kbd> + <kbd>F8</kbd>|Replace all occurrences|

### Commands for Project Explorer

These key combinations work when the Project Explorer dialog-box is active:

| Key | Action |
|-----|--------|
|<kbd>Ctrl</kbd> + <kbd>R</kbd>|Refresh file tree|
|<kbd>Ctrl</kbd> + <kbd>N</kbd>|Create a new file under the selected directory|
|<kbd>Ctrl</kbd> + <kbd>D</kbd>|Create a new directory under the selected directory|
|<kbd>F2</kbd>|Rename the selected file/directory|
|<kbd>Del</kbd>|Moves the selected file/directory to the trash|
|<kbd>+</kbd>|Collapse the current selected directory|
|<kbd>-</kbd>|Expand the current selected directory|

## Other features

**ash** also provides certain shortcuts for helping in editing code. It has support for auto-indentation when the previous line is indented. Also, pressing any of theese keys: <kbd>\`</kbd> <kbd>\'</kbd> <kbd>\"</kbd> <kbd>\(</kbd> <kbd>\{</kbd> <kbd>\[</kbd> while some text is selected, will cause **ash** to enclose the selected text within the pair of matching quotes/brackets.

All of these key bindings can be changed by editing the file `~/.ash-editor/keymappings.txt`.