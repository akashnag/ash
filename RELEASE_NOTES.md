<!--
	Copyright (c) Akash Nag. All rights reserved.
	Licensed under the MIT License. See LICENSE.md in the project root for license information.
-->

# Release Notes

| Version | Release Date |
|---------|--------------|
| [0.1.0-dev14](#10th-august-2022-release) | 2022-08-10 |
| [0.1.0-dev13](#6th-august-2022-release) | 2022-08-06 |
| 0.1.0-dev12 | 2022-02-20 |
| 0.1.0-dev11 | 2022-02-06 |
| 0.1.0-dev10 | 2022-01-25 |


## 10th August 2022 Release

### New features

#### Multi-language support

From this release, **ash** now supports multiple languages. You can add language files (in JSON format) and extend the language support. By default, **ash** only supports `en-US`. To know more about how you can create and add language files, see [Adding language support](CUSTOMIZATION.md#adding-languages).

#### Support for Snippets

From this release, **ash** now supports snippets. You can add your own snippets and then insert them any where in your text. To add a defined snippet, select `Edit` > `Insert snippet`. In the dialog-box which opens you can type to search a snippet name. The list of snippets matching your search will appear in the list below. You can type the full snippet name and press Enter, or move to the list and select a snippet and press Enter to insert the snippet. Besides the snippet name, you can also type its numeric ID for a faster snippet selection. To know more about how you can create and add snippets to **ash**, see [Adding snippets](CUSTOMIZATION.md#adding-snippets).

#### Improved mouse support

Mouse support has been further improved. Now you can:

- Double-click to select a word, triple-click to select a line in the editor
- Move cursor up/down in the editor using the mouse-wheel
- Scroll up/down in lists in all dialog-boxes
- Drag the mouse to select text in the editor

#### Supported file types are now customizable

Before opening a file, **ash** checks its MIME-type to determine whether or not it is a binary or a text file. Binary files can not be opened in **ash**. The list of supported MIME-types were pre-defined. Also, **ash** did not take into consideration the file extension to determine whether or not it is a text file. This now changes. From this release, **ash** both MIME-types as well as file-extensions will be checked. And both of these lists (i.e. list of supported MIME types and list of supported file-extensions) are now customizable in settings.

### Bug fixes

#### Menus and close-buttons are now clickable

Due to a bug introducted in the previous version, menu-bar, popup-menus and close-buttons were rendered unclickable. Now the bug has been fixed.

#### Settings, theme files, etc. were missing the last line

JSON files created by **ash** were missing a line-feed character at the end, and the last line was not being displayed in the editor when those files were loaded. Now, **ash** will add a new line to the end of every file it creates. (Note: files created using other editors which do not add the newline at the end, will still be displayed incorrectly.)

#### Project Explorer search functionality fixed

The search functionality in Project Explorer was not able to perform correctly. This has now been fixed.

#### Invisible text in lists fixed

Due to a bug in the color module, some texts in list-boxes were rendered invisible (e.g. in Project Explorer and Find/Replace in all files). This has now been fixed.

#### Other bug fixes

Sometimes the editor crashed when the menu bar changed state from visible to hidden after selecting an item. This has now been fixed.

### Other changes

#### Adding themes and keymaps are now easier

Creating new themes and keymaps, and applying them are now straight-forward. To know how you can create and apply themes and keymaps, see [Customization](CUSTOMIZATION.md).

#### Menu revamped

The **ash** menu has been redesigned with some menu items shifted, some menus renamed, and others like `Close` and `Reload from disk` options added.

<!------------------------------------------------------------------------------------>

## 6th August 2022 Release

### New features

#### Improved mouse support

Mouse support has been improved. Clicking on the title-bar will now show the menu-bar. Right-clicking on a line of text in the editor will now show the context-menu. Clicking on an inactive editor will now move the focus to that editor. Clicking on any text will move the cursor to that position. Dialog-boxes can now be dragged using their title-bars.

### Bug fixes

#### Error on writing to write-protected file
	
The application would crash if a write-protected file were to be opened and then attempts are made to save to it. This is now resolved. An error message is now displated to the user if they try to save any changes to the file. Users can then try to save the file with a different name if they so choose.

#### File deleted externally

If a currently opened file is deleted externally, <b>ash</b> would now inform the user and let them choose what to do with the file. If they choose to recreate the file, it will be recreated. Otherwise, the contents will be transferred to a new unfiled buffer.

### Other changes

#### Settings moved to `~/.config` on Linux
	
<a href="https://github.com/domsch1988">@domsch1988</a><br/>

All settings, keymaps, theme files, etc. have now been moved from `~/.ash-editor` to `~/.config/ash-editor`. <a href="https://github.com/akashnag/ash/pull/17">PR #17</a>
