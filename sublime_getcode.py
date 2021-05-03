import argparse
import html.parser
import queue
import requests
import sublime
import sublime_plugin
import sys
import threading

# To install the dependencies.json into the Sublime Text software, do the following:
# Type Ctrl+Shift+P
# Type Package Control: Satisfy Dependencies

def getcode(codeQueue, keywords):

  class SearchPageParser(html.parser.HTMLParser):

    isResult = False
    webAddresses = []

    def handle_starttag(self, tag, attrs):
      if tag == "a":
        if ("class", "result__url") in attrs:
          self.isResult = True

    def handle_endtag(self, tag):
      if tag == "a":
        self.isResult = False

    def handle_data(self, data):
      if self.isResult:
        self.webAddresses.append(data.strip())

  class CodePageParser(html.parser.HTMLParser):

    isCode = False

    def handle_starttag(self, tag, attrs):
      if tag in ["code"]:
        self.isCode = True
      if tag == "td":
        attrsDict = dict(attrs)
        if "class" in attrsDict:
          classString = attrsDict["class"]
          words = classString.split(" ")
          if "blob-code" in words:
            self.isCode = True
      if codeQueue.maxsize > 0 and tag == "br" and self.isCode:
        codeQueue.put("")
        codeQueue.maxsize -= 1

    def handle_endtag(self, tag):
      if tag in ["code", "td"] and self.isCode:
        self.isCode = False
        if codeQueue.maxsize > 0:
          codeQueue.put("")
          codeQueue.maxsize -= 1

    def handle_data(self, data):
      if self.isCode:
        data_lines = data.split("\n")
        for data_line in data_lines:
          if codeQueue.maxsize > 0:
            codeQueue.put(data_line)
            codeQueue.maxsize -= 1

  searchAddress = "https://html.duckduckgo.com/html?q={}".format(keywords)
  searchPageParser = SearchPageParser()
  searchPageParser.feed(requests.get(searchAddress, headers={"user-agent": "getcode/0.0.1"}).text)

  codeQueue.put("Fetching the first lines of Internet code described by \"{}\"".format(keywords))
  codeQueue.put("--------------------------------------------------")
  codeQueue.put(searchAddress)
  codeQueue.maxsize -= 3

  codePageParser = CodePageParser()
  for webAddress in searchPageParser.webAddresses:

    if codeQueue.maxsize == 0: break

    codeQueue.put("==================================================")

    webAddressWithProtocol = "http://" + webAddress
    codeQueue.put(webAddressWithProtocol)
    codeQueue.maxsize -= 2

    try:
      codePageParser.feed(requests.get(webAddressWithProtocol).text)
    except requests.exceptions.ConnectionError as exception:
      print("GETCODE ERROR requests.exceptions.ConnectionError: " + str(exception), file=sys.stderr)

  codeQueue.put("STOP")

class KeywordsInputHandler(sublime_plugin.TextInputHandler):

  def placeholder(self):
    return "Describe desired code."

class GetcodeCommand(sublime_plugin.TextCommand):

  def input(self, args):
    return KeywordsInputHandler()

  def run(self, edit, keywords):

    codeQueue = queue.Queue(120)

    fetchingThread = threading.Thread(name="Page-Parser", target=getcode, args=(codeQueue, keywords,))
    fetchingThread.start()

    window = sublime.active_window()
    fetching_view = window.new_file()
    window.focus_view(fetching_view)

    for code_line in iter(codeQueue.get, "STOP"):
      fetching_view.run_command("append", {"characters": code_line + "\n"})
