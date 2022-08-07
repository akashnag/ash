<!--
	Copyright (c) Akash Nag. All rights reserved.
	Licensed under the MIT License. See LICENSE.md in the project root for license information.
-->

# Release Notes

| Version | Release Date |
|---------|--------------|
| [0.1.0-dev13](#6th-august-2022-release) | 2022-08-06 |
| 0.1.0-dev12 | 2022-02-20 |
| 0.1.0-dev11 | 2022-02-06 |
| 0.1.0-dev10 | 2022-01-25 |


## 6th August 2022 Release

### Bug fixes

<dl>
	<dt>Error on writing to write-protected file</dt>
	<dd>
	<em>Contributors:</em>
	<a href="https://github.com/akashnag"><img src="https://avatars.githubusercontent.com/u/48851399?v=4" height="20" style="border-radius:20px"/></a><br/>
	The application would crash if a write-protected file were to be opened and then attempts are made to save to it. This is now resolved. An error message is now displated to the user if they try to save any changes to the file. Users can then try to save the file with a different name if they so choose.</dd>	  
	<dt>File deleted externally</dt>
	<dd>
	<em>Contributors:</em>
	<a href="https://github.com/akashnag"><img src="https://avatars.githubusercontent.com/u/48851399?v=4" height="20" style="border-radius:20px"/></a><br/>
	If a currently opened file is deleted externally, <b>ash</b> would now inform the user and let them choose what to do with the file. If they choose to recreate the file, it will be recreated. Otherwise, the contents will be transferred to a new unfiled buffer.</dd>
</dl>

### New features

<dl>
	<dt>Improved mouse support</dt>
	<dd>
	<em>Contributors:</em>
	<a href="https://github.com/akashnag"><img src="https://avatars.githubusercontent.com/u/48851399?v=4" height="20" style="border-radius:20px"/></a><br/>
	Mouse support has been improved. Clicking on the title-bar will now show the menu-bar. Right-clicking on a line of text in the editor will now show the context-menu. Clicking on an inactive editor will now move the focus to that editor. Clicking on any text will move the cursor to that position. Dialog-boxes can now be dragged using their title-bars.
	</dd>
</dl>

### Other changes

<dl>
	<dt>Settings moved to ~/.config on Linux</dt>
	<dd>
	<em>Contributors: </em><a href="https://github.com/domsch1988"><img src="https://avatars.githubusercontent.com/u/1961154?v=4" height="20" style="border-radius:20px"/></a><br/>
	All settings, keymaps, theme files, etc. have now been moved from ~/.ash-editor to ~/.config/ash-editor
	</dd>
</dl>
