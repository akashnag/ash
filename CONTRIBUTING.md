# Contribution Guidelines

This section contains the list of known bugs and features that are on the roadmap for implementation. If you want to contribute to this project, please start here:

## Known bugs
- Syntax highlighting is broken

## Features to be implemented
- Syntax highlighting for common languages
- Git integration
- View a list of files recently opened
- Auto-completion/Suggestions
- Plugin system
- Macros
- Command palette

If you find any issue, please report it first and then consider if you can solve it yourself. If so, please make a PR.

If you can help with implementing any of the features above, please make a PR, or contact me on [Gitter](https://gitter.im/akashnag/ash) for more information.

## Project Struture

The source code for the project is in the `/ash/src` folder. It uses the curses library to perform all screen-drawing functions. The project contains the following packages:
1. `ash`: the root package
2. `ash.core`: contains the back-end of the application
3. `ash.gui`: containst the front-end of the application
4. `ash.formatting`: contains all color, syntax-highlighting, etc. related modules
5. `ash.utils`: contains all miscellaneous modules

The entry point for the application is `/ash/src/ash.py`.