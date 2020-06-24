![ash logo](./assets/banner.png)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/akashnag/ash/blob/master/LICENSE.md) ![Downloads](https://img.shields.io/github/downloads/akashnag/ash/total)

**ash** is a simple and clean terminal-based text editor for Linux, that aims to be easy to use with modern key-bindings. It is fully capable of handling multiple files simultaneously and hopes to provide a wide array of features when it is released.

Here is a picture of **ash** editing this README file:

![Screenshot](./assets/ash-default.png)

**ash** is written in Python 3.8 using the curses library. It is a work-in-progress and hopefully the first release will be out there soon.

## Table of Contents

- [Design Goals](#design-goals)
- [Installation](#installation)
  - [Prebuilt binaries](#prebuilt-binaries)
  - [Linux clipboard support](#linux-clipboard-support)
  - [Colors and syntax highlighting](#colors-and-syntax-highlighting)
  [Usage](#usage)
- [Documentation and Help](#documentation-and-help)
- [Contributing](#contributing)

- - -

## Design Goals

The following is a list of design goals for ash; some of which have already been implemented, while some are yet to be:

- Easy to use.
- No dependencies.
- Common keybindings.
- Support for wide variety of splits.
- Simple autocompletion.
- Syntax highlighting.
- Color scheme support.
- Copy and paste with the system clipboard.
- Macros.
- Common editor features such as undo/redo, line numbers, Unicode support, soft wrapping, …
- Auto-backup.
- Encryption.
- File transfer over TCP/UDP.

## Installation

As **ash** is still in development, there are no prebuilt binaries available for download. However, if you have python 3.8 installed on your system, you are ready to go and download **ash**. For Linux users, follow the following steps to get **ash** on your system:

```bash
$ cd ~
$ git clone --depth 1 -b master https://github.com/akashnag/ash.git
$ cd ash/bin
$ sudo chmod +x ash
```

Then add `ash/bin` to your path by editing your `.bashrc` file:

```bash
$ sudo nano ~/.bashrc
```

Then append `:~/ash/bin` to the `PATH` variable. You are now ready to run **ash** from the terminal. See [Usage](#usage) for details.

### Prebuilt binaries

Since **ash** is still under development, prebuilt binaries are not yet available.

### Clipboard support

On Linux, clipboard support requires:

- On X11, the `xclip` or `xsel` commands (for Ubuntu: `sudo apt install xclip`)

If you do not have these installed on your system, **ash** will use an internal clipboard for clipboard operations, but the data will not be available in external applications.

### Colors

If you are using the default Ubuntu terminal, to enable 256 make sure your `TERM` variable is set to `xterm-256color`.

## Usage

Once you have downloaded the **ash** source code, and set it up as detailed above, you are ready to use it:

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

See the [key-bindings](KEYBINDINGS.md) for help on how to navigate in ash.

## Contributing

If you find any bugs, please report them. I am also happy to accept pull requests from anyone. For more information on what features to implement and the project structure, see the [Contribution Guidelines](CONTRIBUTING.md)

You can use the [GitHub issue tracker](https://github.com/akashnag/ash/issues) to report bugs, ask questions, or suggest new features.

For discussions related to the development roadmap and the **ash** editor in general, you can join the [Gitter chat](https://gitter.im/akashnag/ash).

## License

Copyright &copy; Akash Nag. All rights reserved.

Licensed under the [MIT](LICENSE.md) license.