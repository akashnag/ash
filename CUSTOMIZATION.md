<!-- SPDX-License-Identifier: GPL-2.0-only -->
<!--
/CUSTOMIZATION.md

Copyright (C) 2022-2022  Akash Nag
-->

# Customizing ash

You can customize **ash** to make it look and feel the way you want it to. This document will describe the process for customizing **ash** in 4 parts:

- [Adding languages](#adding-languages)
- [Adding snippets](#adding-snippets)
- [Adding themes](#adding-themes)
- [Adding keymaps](#adding-keymaps)

## Adding languages

**ash** has multi-language support but by default supports only `en-US`. If you want to add more languages, you can either create those language files yourself, or check any repository which may already provide it. Once you have created or downloaded the language files, place them in your **ash** locale-settings folder which is `~/.config/ash-editor/locales/`. If you have launched **ash** once before, you should already see a file `en-US.json` here.

### Creating more language files

Navigate to the `~/.config/ash-editor/locales/` directory where you will find a file called `en-US.json`. If you can't find the file, launch **ash** once, and the file will get created automatically. This file is your template from which you can create other language files.

Let us say you want to create a French language file. Make a copy of the `en-US.json` file and name it `fr.json`. Open the `fr.json` in **ash** or any other text-editor. You will see something like this:

```json
{
    "File": "File",
    "Edit": "Edit",
	...
}
```

Each line in the file contains a key-value pair where the key (on the left) is the English text and the value (on the right) is the translated text. Replace the value on the right with a French translation. Once you have translated the whole file, it should look like this:

```json
{
    "File": "Fichier",
    "Edit": "Edition",
	...
}
```

Save the file and close it. You have successfully added French language support to **ash**!

### Changing the UI language

Launch **ash** and go to `Edit` > `Global Settings...`. You will see the `settings.json` file opened in the editor: 

*Note: you can also edit the file `~/.config/ash-editor/settings.json` directly in any text-editor as an alternative.*

```json
{
    "ui_language": "en-US",
    "theme": "default_theme",
    "keymap": "default_keymap",
	...
}
```

Change the `ui-language` setting to `fr` so that it looks like this:

```json
{
    "ui_language": "fr",
    "theme": "default_theme",
    "keymap": "default_keymap",
	...
}
```

Save the file using <kbd>Ctrl</kbd> + <kbd>S</kbd> (or, from `File` > `Save`). You will see the changes immediately. Your `File` menu should now read as `Fichier`. You have now successfully changed the UI language.

## Adding snippets

Snippets are blocks of text which you frequently type in. Instead of typing it manually every time, you can now save it as a snippet and insert the whole block just with a few keystrokes.

### Creating new snippets

Snippets are stored in the `~/.config/ash-editor/snippets/` directory. Navigate to this directory where you will see snippet files which you have created earlier, if any. Each snippet file is named as `<filetype>.snippets`. E.g. Snippets for Javascript will be stored in the `js.snippets` file, while those for C++ will be in `cpp.snippets`, `h.snippets` or `hpp.snippets` files. Choose a language you want to create snippets for. For this example, we will create two snippets for Java.

Open the file `java.snippets` (or create it if it doesn't exist) in a text-editor. Each snippet-block begins with `snippet <snippet-name>` and ends with `endsnippet` lines. Let us create the following two snippets:

```
snippet hello_world
class MyClass
{
	public static void main(String args[])
	{
		System.out.println("Hello World!);
	}
}
endsnippet

snippet br_input
import java.io.*;
class Greeting
{
	public static void main(String args[]) throws IOException
	{
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

		System.out.print("Enter your name: ");
		String name = br.readLine();

		System.out.println("Hello " + name + "! Welcome to Java.");
	}
}
endsnippet
```

Save the file and close it. Thus we have successfully created two Java snippets by the name `hello_world` and `br_input`.

### Inserting snippets into the current document

Launch **ash**. Open an editor (if not already) where you want to insert a snippet. Save the file as a Java file (with a `.java` extension). Place your cursor in the proper position where you want the snippet to get inserted. Then go to `Edit` > `Insert Snippet...`. You will see a dialog-box appears. There is a textbox for which to search for a snippet. Below you will find a list of snippets, each snippet name being prefixed by an ID within square brackets. If everything works out, you should see the two snippets we created earlier. Now, either you can select a snippet from the list or you can type its name (or its ID). e.g. You can just type `1` and press <kbd>Enter</kbd>. The dialog-box will then disappear, and your chosen snippet will be inserted in your code.

## Adding themes

**ash** lets you customize the colors in the editor. (Note: ensure that you are using a terminal which supports colors. Try setting your `TERM` variable to something like `xterm-256color` if you don't see colors in **ash**). Each color scheme is called a theme, and you can create your own themes or download one from any repository you may find. The default theme is stored in the file `~/.config/ash-editor/themes/default_theme.json`.

### Creating your own themes

Open the `~/.config/ash-editor/themes/` directory and you will see a file `default_theme.json`. If you don't see the file, launch **ash** and the file will get created automatically. This file is the template you can use to build your own themes. Suppose you want to create your own theme called `my_theme`. Make a copy of the `default_theme.json` and name it `my_theme.json` and open it in a text-editor. You should see something like this:

```json
{
    "colors": {
        "darkgray": "rgb(28, 28, 28)",
        "lightgray": "rgb(132, 132, 132)",
        ...
    },
    "elements": {
        "background": "(dimwhite, darkgray)",
        "editor-background": "(dimwhite, darkgray)",
		...
	}
}
```

The theme file contains two sections: `colors` and `elements`. The `colors` section defines the names of colors and its values. You can name the color anything you want, e.g. you can change `darkgray` to `purple`, and change its color value. The color value is in RGB (red-green-blue) format with each of the 3 components ranging between 0 and 255 (both inclusive). Once you have defined your colors, you can change the colors of each of the UI elements in the `elements` section. e.g. `editor-background` refers to the main editor writing-space. By default it is dark-gray (background) in color, with text on it being in dim-white (foreground). You can change the default value to some other `(foreground, background)` combination you like. These foreground and background names must be one of the colors you defined in the `colors` section earlier. After you have done the changes, save and close the file.

### Applying a theme

Launch **ash** and go to `Edit` > `Global Settings...`. You will see the `settings.json` file opened in the editor:

*Note: you can also edit the file `~/.config/ash-editor/settings.json` directly in any text-editor as an alternative.*

```json
{
    "ui_language": "en-US",
    "theme": "default_theme",
    "keymap": "default_keymap",
	...
}
```

Change the `theme` setting to `my_theme` so that it looks like this:

```json
{
    "ui_language": "en-US",
    "theme": "my_theme",
    "keymap": "default_keymap",
	...
}
```

Save the file using <kbd>Ctrl</kbd> + <kbd>S</kbd> (or, from `File` > `Save`). You should be able to see the color changes immediately. You have now successfully changed the UI theme.


## Adding keymaps

**ash** lets you remap the keyboard shortcuts to your liking. For this, you can either download a keymap file (from any repository you may find) or create one yourself. **ash** is based on the Curses library, and you may want to check out the keycodes that curses uses.

### Creating your own keymaps

Keymaps are stored in the `~/.config/ash-editor/keymaps/` directory. There you will find a file called `default_keymap.json` containing the default keymap. If you don't see the file, launch **ash** and the file will get created automatically. To create your own keymaps, you can use this file as your starting point. To create your own keymap, say `my_keymap`, first make a copy of this file and rename it to `my_keymap.json`. Then open this file in a text-editor. You will see something like this:

```json
{
    "CLOSE_WINDOW": {
        "curses_keycode": "^Q",
        "key_name": "Ctrl+Q",
        "description": "Close the active window"
    },
    ...
}
```

Each command in this JSON (e.g. `CLOSE_WINDOW` is a command) has 3 parts: `curses_keycode`, `key_name` and `description`. The `curses_keycode` is what you would want to change by putting the code for the new shortcut. For example, closing dialog-boxes shortcut is mapped to <kbd>Ctrl</kbd> + <kbd>Q</kbd> by default. <kbd>Ctrl</kbd> keys are usually represented by a carat (`^`) symbol. If you want to remap it to, say, <kbd>Ctrl</kbd> + <kbd>X</kbd>, then replaec `^Q` with `^X`. You should also change the `key_name` from `Ctrl+Q` to `Ctrl+X` which is just a human-readable name for the key for other people to understand what to press on the keyboard. This name will be displayed in the `Help` > `Key Bindings...` dialog-box, along with the `description`. Once you are happy with the changes, save and close the file.

### Changing the current keymap

Launch **ash** and go to `Edit` > `Global Settings...`. You will see the `settings.json` file opened in the editor:

*Note: you can also edit the file `~/.config/ash-editor/settings.json` directly in any text-editor as an alternative.*

```json
{
    "ui_language": "en-US",
    "theme": "default_theme",
    "keymap": "default_keymap",
	...
}
```

Change the `keymap` setting to `my_keymap` so that it looks like this:

```json
{
    "ui_language": "en-US",
    "theme": "default_theme",
    "keymap": "my_keymap",
	...
}
```

Save the file using <kbd>Ctrl</kbd> + <kbd>S</kbd> (or, from `File` > `Save`). You need to restart **ash** for the changes to take effect. You have now successfully changed the key binding.
