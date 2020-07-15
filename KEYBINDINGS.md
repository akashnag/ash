# Key Bindings for ash

The following is a list of key bindings for **ash**.

### Global key combinations

These key combinations can be used even if no editor is currently active.

| Key | Action |
|-----|--------|
|<kbd>Ctrl</kbd> + <kbd>Q</kbd>|Closes the active window|
|<kbd>Ctrl</kbd> + <kbd>@</kbd>|Forcefully quits the application, discarding all changes|
|<kbd>Tab</kbd>|Moves focus to the next widget in the active dialog-box (if any)|
|<kbd>Shift</kbd> + <kbd>Tab</kbd>|Moves focus to the previous widget in the active dialog-box|
|<kbd>Ctrl</kbd> + <kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Moves the active dialog-box (if any) around the screen|
|<kbd>Space</kbd>|Checks/Unchecks a selected checkbox|
|<kbd>Enter</kbd> _or_ <kbd>Ctrl</kbd> + <kbd>W</kbd>|Saves changes and closes the current dialog box|
|<kbd>Ctrl</kbd> + <kbd>L</kbd>|Changes the layout of splits|
|<kbd>Ctrl</kbd> + <kbd>N</kbd>|Opens a new buffer|
|<kbd>Ctrl</kbd> + <kbd>O</kbd>|Open a file|
|<kbd>Ctrl</kbd> + <kbd>E</kbd>|Opens project explorer (if directory has been opened)|
|<kbd>F1</kbd> - <kbd>F6</kbd>|Activates the corresponding editor (if exists in the current layout)|
|<kbd>F12</kbd>|Shows the list of recently opened files|
|<kbd>Ctrl</kbd> + <kbd>F1</kbd>|Shows the key-bindings|

Apart from the above, selection and cursor-movement using <kbd>Shift</kbd> and/or arrow / <kbd>Home</kbd> / <kbd>End</kbd> keys, as well as Cut / Copy / Paste (using <kbd>Ctrl</kbd> + <kbd>X</kbd> / <kbd>C</kbd> / <kbd>V</kbd> respectively) work in all text-fields (wherever they occur in dialog-boxes).

### Editor commands

These key combinations work only if an editor is currently active.

| Key | Action |
|-----|--------|
|<kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Moves the cursor in the document one character/line at a time|
|<kbd>Ctrl</kbd> + <kbd>&#8592;</kbd> <kbd>&#8594;</kbd>|Moves the cursor one word at a time|
|<kbd>PgUp</kbd> <kbd>PgDown</kbd>|Moves the cursor in the document one screenful at a time|
|<kbd>Home</kbd> <kbd>End</kbd>|Moves the cursor to the beginning/end of the current line|
|<kbd>Ctrl</kbd> + <kbd>Home</kbd> <kbd>End</kbd>|Moves the cursor to the beginning/end of the current document|
|<kbd>Tab</kbd>|When some text is selected, it increases the indent of the selection|
|<kbd>Shift</kbd> + <kbd>Tab</kbd>|When some text is selected, it decreases the indent of the selection if possible|
|<kbd>Shift</kbd> + <kbd>Home</kbd> <kbd>End</kbd>|Selects text up to the beginning/end of the current line|
|<kbd>Shift</kbd> + <kbd>&#8592;</kbd> <kbd>&#8593;</kbd> <kbd>&#8594;</kbd> <kbd>&#8595;</kbd>|Selects text one character at a time|
|<kbd>Shift</kbd> + <kbd>PgUp</kbd> <kbd>PgDown</kbd>|Selects one screenful at a time|
|<kbd>Ctrl</kbd> + <kbd>A</kbd>|Select all|
|<kbd>Ctrl</kbd> + <kbd>C</kbd>|Copy|
|<kbd>Ctrl</kbd> + <kbd>X</kbd>|Cut|
|<kbd>Ctrl</kbd> + <kbd>V</kbd>|Paste|
|<kbd>Backspace</kbd>|Deletes the character/selected-text before the cursor|
|<kbd>Del</kbd>|Deletes the selected-text or, character at the cursor position|
|<kbd>Ctrl</kbd> + <kbd>F2</kbd>|Convert all Uncode escape sequences and also sets file encoding to UTF-8|
|<kbd>Ctrl</kbd> + <kbd>S</kbd>|Saves the current file|
|<kbd>Ctrl</kbd> + <kbd>W</kbd>|Save and Close|
|<kbd>F9</kbd>|Save As...|
|<kbd>Ctrl</kbd> + <kbd>P</kbd>|Opens the preferences dialog-box|
|<kbd>Ctrl</kbd> + <kbd>G</kbd>|Go to a given line/column|
|<kbd>Ctrl</kbd> + <kbd>Z</kbd>|Undo|
|<kbd>Ctrl</kbd> + <kbd>Y</kbd>|Redo|
|<kbd>Ctrl</kbd> + <kbd>F</kbd>|Find|
|<kbd>Ctrl</kbd> + <kbd>H</kbd>|Replace|

### Commands for find and replace operations

These key combinations work when the Find/Replace dialog box is active:

| Key | Action |
|-----|--------|
|<kbd>Enter</kbd>|Find next match|
|<kbd>F7</kbd>|Find previous match|
|<kbd>F8</kbd>|Replace the current match|
|<kbd>Ctrl</kbd> + <kbd>F8</kbd>|Replace all matches|

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