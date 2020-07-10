![ash logo](./assets/banner.png)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/akashnag/ash/blob/master/LICENSE.md) ![Downloads](https://img.shields.io/github/downloads/akashnag/ash/total)

**ash** is a simple and clean terminal-based text editor for Linux and macOS, that aims to be easy to use with modern key-bindings. It is fully capable of handling multiple files simultaneously and hopes to provide a wide array of features when it is released.

Here is a picture of **ash** editing this README file (syntax highlighting is not yet implemented):

![Screenshot](./assets/ash-default.png)

**ash** is written in Python 3.8 using the curses library. It is a work-in-progress and hopefully the first release will be out there soon.

## Table of Contents

- [Design Goals](#design-goals)
- [Installation](#installation)
  - [Prebuilt binaries](#prebuilt-binaries)
  - [Clipboard support](#clipboard-support)
  - [Colors](#colors)
  - [Usage](#usage)
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

The following is a list of features available in **ash**; some of which have already been implemented, while some are yet to be:

**Already implemented:**

- Common editor features such as undo/redo, line numbers, find-replace, cut-copy-paste, etc.
- True support for wrapping (both hard & soft) with intuitive cursor movements along wrapped text
- Auto-backup
- Support for Unicode
- Project mode (opening a directory instead of individual files)
- Support for splits/windows
- Support for various text-encodings
- Syntax highlighting
- Selection highlighting (highlights text under selection wherever they occur in the document)
- Color scheme customization

**Not yet implemented:**

- View list of recent files
- Git integration

**Future goals:**

- Macros and command-palette
- Autocompletion/Suggestions
- Integrated terminal
- Plugin system

## Installation

As **ash** is still in development, there are no prebuilt binaries available for download. However, if you have python 3.8 installed on your system, you can download and run a developmental build for **ash**. For Linux users, follow the following steps to get **ash** on your system:

#### Prerequisites

You need certain packages and Python 3 itself to download and run the developmental build:

```bash
$ sudo apt install git
$ sudo apt install xclip
$ sudo apt install python3
$ sudo apt install python3-pip
```

#### Downloading and setting up ash

```bash
$ cd ~
$ git clone --depth 1 -b master https://github.com/akashnag/ash.git
$ cd ash/bin
$ sudo chmod +x ash
$ cd ..
$ sudo pip3 install -r requirements.txt
```

To be able to launch **ash** from anywhere, you need to add `~/ash/bin` to your path by editing your `.bashrc` file:

```bash
$ sudo nano ~/.bashrc
```

Then append `:~/ash/bin` to the `PATH` variable. You are now ready to run **ash** from the terminal. See [Usage](#usage) for details.

### Prebuilt binaries

Since **ash** is still under development, prebuilt binaries are not yet available.

### Colors

If you are using the default Ubuntu terminal, to enable 256 make sure your `TERM` variable is set to `xterm-256color`. After **ash** runs for the first time, it creates a `.ashrc` file inside your home directory. You can edit that file directly to change how **ash** looks on your system. The RGB triplets listed in that file range from 0--255. If you want to reset **ash** to its default colors, delete the configuration file using: `rm ~/.ashrc`.

## Usage

Once you have downloaded the **ash** source code, and set it up as detailed above, you are ready to use it (it may take some time to load for the first time) **NOTE: if you have not updated your path variable, you must specify the full path to the ash binary.**

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

See the [Key Bindings](KEYBINDINGS.md) for help on how to navigate in ash.

## Contributing

If you find any bugs, please report them. I am also happy to accept pull requests from anyone for either bug-fixes, performance improvements, or for implementing the not-yet-implemented features listed above. Please consider contributing towards new features **only when** the features listed above have been fully implemented. For more information on what features to implement and the project structure, see the [Contribution Guidelines](CONTRIBUTING.md)

You can use the [GitHub issue tracker](https://github.com/akashnag/ash/issues) to report bugs, ask questions, or suggest new features.

For discussions related to the development roadmap and the **ash** editor in general, you can join the [Gitter chat](https://gitter.im/akashnag/ash).

## Screenshots

![Screenshot](./assets/ss1.png)
![Screenshot](./assets/ss2.png)
![Screenshot](./assets/ss3.png)
![Screenshot](./assets/ss4.png)
![Screenshot](./assets/ss5.png)

## License

Copyright &copy; Akash Nag. All rights reserved.

Licensed under the [MIT](LICENSE.md) license.