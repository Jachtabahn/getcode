# Just run the getcode.py script, putting the results into a separate file, and open that file with Sublime Text
# for easy viewing of valuable code from the Internet.

import sublime
import sublime_plugin
import subprocess
import tempfile

# Put
# { "keys": ["ctrl+shift+g"], "command": "getcode" },
# into the file, that opens when you go to Preferences -> Key Bindings, which is at
# `~.config/sublime-text-3/Packages/User/Default (Linux).sublime-keymap`.

# Put
# [
#   { "caption": "Get code", "command": "getcode" },
# ]
# into a file called `getcode.sublime-commands`
# inside the same folder as this file.

# To install the dependencies.json into the Sublime Text software, do the following:
# Type Ctrl+Shift+P
# Type Package Control: Satisfy Dependencies

class KeywordsInputHandler(sublime_plugin.TextInputHandler):

  def placeholder(self):
    return "Describe desired code."

class GetcodeCommand(sublime_plugin.TextCommand):

  def input(self, args):
    return KeywordsInputHandler()

  def run(self, edit, keywords):

    # Erstelle selbst einen Dateinamen, welcher den Befehlstext enthält.
    # `keywords` is of type <class 'str'>
    tempdir_path = tempfile.gettempdir()
    zusammen = keywords.replace(' ', '_')

    code_path = tempdir_path + '/' + zusammen

    with open(code_path, 'w') as code_file:
      proc = subprocess.Popen(['getcode', keywords], stdout=code_file, stderr=code_file)

    window = sublime.active_window()
    fetching_view = window.open_file(code_path)
    # Set title of fetching_view with `keywords`
    window.focus_view(fetching_view)
