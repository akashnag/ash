<!--
	Copyright (c) Akash Nag. All rights reserved.
	Licensed under the MIT License. See LICENSE.md in the project root for license information.
-->

# Contribution Guidelines

This section contains the list of known bugs and features that are on the roadmap for implementation. If you want to contribute to this project, please start here. If you want to contribute, please consider contributing in the following order:

1. Major issues to be resolved
1. Major changes required
1. New features to be implemented

## Major issues to be resolved

1. Performance is unacceptable when both soft-wrap and syntax-highlighting are turned on

## Major changes required

1. Implement a borderless *Frame* widget which can house other widgets (including Editors). Currently, only windows can contain other widgets.
1. TabNode currently can host only editors; must be able to handle a Frame.

## New features to be implemented

1. Dockable project-explorer, search, etc. like Visual Studio Code, subject to screen-space*
1. Integrated terminal*
1. Command palette
1. Auto-completion/Suggestions
1. Plugin system
1. Reading from standard input
1. Macros
1. Porting to Windows 10+

\* *Requires implementation of the Frame widget first*

If you find any issue, please report it first before submitting a PR. If you can help with implementing any of the features above (prioritize issues and major changes, before moving on to new features), please submit a PR, or contact me on [Gitter](https://gitter.im/akashnag/ash) for more information.

## Design Goals

The long-term goal for this project is to be a [VS Code](https://code.visualstudio.com/) alternative for the terminal.

## Project Struture

The source code for the project is in the `/ash/src` folder. It uses the curses library to perform all screen-drawing functions. The project contains the following packages:

1. `ash`: the root package
2. `ash.core`: contains the back-end of the application
3. `ash.gui`: containst the front-end of the application
4. `ash.formatting`: contains all color, syntax-highlighting, etc. related modules
5. `ash.utils`: contains all miscellaneous modules

The entry point for the application is `/ash/src/ash/ash_main.py`
