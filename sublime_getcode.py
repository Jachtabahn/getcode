# Just run the getcode.py script, putting the results into a separate file, and open that file with Sublime Text
# for easy viewing of valuable code from the Internet.

import os
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

    code_keywords_filepath = os.path.join(tempfile.gettempdir(), 'getcode.keywords')

    with open(code_keywords_filepath, 'w') as code_file:
      code_keywords = keywords.split()
      proc = subprocess.Popen(
        ['getcode'] + code_keywords,
        stdout=code_file,
        stderr=code_file
      )

    window = sublime.active_window()
    fetching_view = window.open_file(code_keywords_filepath)
