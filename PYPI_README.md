![ash logo](https://github.com/akashnag/ash/raw/master/assets/banner.png)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/akashnag/ash/blob/master/LICENSE.md) ![Downloads](https://img.shields.io/github/downloads/akashnag/ash/total) ![Size](https://img.shields.io/github/size/akashnag/ash/dist/ash-editor-0.1.0.dev4.tar.gz) ![SLOC](https://sloc.xyz/github/akashnag/ash)

**ash** is a simple and clean terminal-based text editor, that aims to be easy to use with modern key-bindings. It is capable of handling multiple files simultaneously and has a wide array of modern features. Here is a picture of **ash** editing this README file:

![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ash-default.png)

**ash** is written in Python 3.8 using the curses library. View this project on GitHub: [ash on GitHub](https://github.com/akashnag/ash)

## Table of Contents

- [Design Goals](#design-goals)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installing **ash**](#installing-ash)
  - [Uninstalling **ash**](#uninstalling-ash)
- [Colors](#colors)
- [Usage](#usage)
- [Key Bindings](#key-bindings)
- [Contributing](#contributing)
- [Screenshots](#screenshots)
- [License](#license)

- - -

## Design Goals

The following is a list of design goals for **ash**:

- Easy to use
- Clean and intuitive interface
- Minimal dependencies
- Common keybindings

**Features:**

The following is a list of features available in **ash**:

- Common editor features such as undo/redo, line numbers, find-replace, cut-copy-paste, etc.
- True support for wrapping (both hard & soft) with intuitive cursor movements along wrapped text
- Auto-backup
- Support for Unicode
- Project mode (opening a directory instead of individual files)
- Support for splits/windows
- Support for various text-encodings
- Selection highlighting (highlights text under selection wherever they occur in the document)
- Color scheme customization
- View list of recent files
- Syntax highlighting (partially implemented)
- Git integration

**Future goals:**

- Macros and command-palette
- Autocompletion/Suggestions
- Integrated terminal
- Plugin system

## Installation

### Prerequisites

You need certain packages and Python 3 itself to download and run the developmental build:

```bash
$ sudo apt install xclip
$ sudo apt install python3
$ sudo apt install python3-pip
```

### Installing ash

```bash
$ sudo pip3 install ash-editor
```

To run **ash** make sure you have `:$HOME/.local/bin` appended to your $PATH variable in the file `~/.bashrc`. To execute **ash**, see the [Usage](#usage) section.

### Uninstalling ash

To uninstall **ash** you can use:

```bash
$ sudo pip3 uninstall ash-editor
```

## Colors

If you are using the default Ubuntu terminal, to enable 256 make sure your `TERM` variable is set to `xterm-256color`. After **ash** runs for the first time, it creates a `.ashedrc` file inside your home directory. You can edit that file directly to change how **ash** looks on your system. The RGB triplets listed in that file range from 0--255. If you want to reset **ash** to its default colors, delete the configuration file using: `rm ~/.ashedrc`.

## Usage

Once you have downloaded **ash**, and set it up as detailed above, you are ready to use it. 

**NOTES:**
1. If you have not updated your path variable, you must specify the full path to the ash binary.
1. Your terminal resolution should be at least 102 (width) x 22 (height). Opening the editor in a lower resolution may unexpectedly crash the application. This requirement is necessary to properly display the dialog-boxes.

To run **ash**:

```bash
$ ash path/to/file.txt
```

or, to open an empty buffer:

```bash
$ ash
```

or, to open a project (directory):

```bash
$ ash path/to/directory
```

## Key Bindings

See the [Key Bindings](https://github.com/akashnag/ash/blob/master/KEYBINDINGS.md)

## Contributing

If you find any bugs, please report them. I am also happy to accept pull requests from anyone for either bug-fixes, performance improvements, or for implementing the not-yet-implemented features listed above. Please consider contributing towards new features **only when** the features listed above have been fully implemented. For more information visit the project's Github page: [ash on GitHub](https://github.com/akashnag/ash)

You can use the [GitHub issue tracker](https://github.com/akashnag/ash/issues) to report bugs, ask questions, or suggest new features.

For discussions related to the development roadmap and the **ash** editor in general, you can join the [Gitter chat](https://gitter.im/akashnag/ash).

## Screenshots

![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ss1.png)
![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ss2.png)
![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ss3.png)
![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ss4.png)
![Screenshot](https://github.com/akashnag/ash/raw/master/assets/ss5.png)

## License

Copyright &copy; Akash Nag. All rights reserved.

Licensed under the [MIT](https://github.com/akashnag/ash/blob/master/LICENSE.md) license.