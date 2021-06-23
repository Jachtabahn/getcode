#!/usr/bin/env python3

# To make this program executable from any process working directory, run:
# ln -s getcode.py ~/.local/bin/getcode

import argparse
import html.parser
import requests
import sys
import threading, queue

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Download some code matching given keywords.')

  parser.add_argument('--num-lines', '-n', type=int, default=30, help='of at least how many lines of the tag node content should be output')
  parser.add_argument('keywords', metavar='N', type=str, nargs='+', help='an integer for the accumulator')

  arguments = parser.parse_args()

  codeQueue = queue.Queue()

  def getcode(keywords):

    class SearchPageParser(html.parser.HTMLParser):

      isResult = False
      webAddresses = []

      def handle_starttag(self, tag, attrs):
        if tag == 'a':
          if ('class', 'result__url') in attrs:
            self.isResult = True

      def handle_endtag(self, tag):
        if tag == 'a':
          self.isResult = False

      def handle_data(self, data):
        if self.isResult:
          self.webAddresses.append(data.strip())

    class CodePageParser(html.parser.HTMLParser):

      isCode = False

      def handle_starttag(self, tag, attrs):
        if tag in ['code']:
          self.isCode = True
        if tag == 'td':
          attrsDict = dict(attrs)
          if 'class' in attrsDict:
            classString = attrsDict['class']
            words = classString.split(' ')
            if 'blob-code' in words:
              self.isCode = True
        if tag == 'br' and self.isCode:
          codeQueue.put("")

      def handle_endtag(self, tag):
        if tag in ['code', 'td'] and self.isCode:
          self.isCode = False
          codeQueue.put("")

      def handle_data(self, data):
        if self.isCode:
          data_lines = data.split("\n")
          for data_line in data_lines:
            codeQueue.put(data_line)

    searchAddress = 'https://html.duckduckgo.com/html?q={}'.format("+".join(keywords))
    searchPageParser = SearchPageParser()
    searchPageParser.feed(requests.get(searchAddress, headers={'user-agent': 'getcode/0.0.1'}).text)

    codeQueue.put("--------------------------------------------------")
    codeQueue.put(searchAddress)

    codePageParser = CodePageParser()
    for webAddress in searchPageParser.webAddresses:

      codeQueue.put("==================================================")

      webAddressWithProtocol = "http://" + webAddress
      codeQueue.put(webAddressWithProtocol)

      try:
        codePageParser.feed(requests.get(webAddressWithProtocol).text)
      except requests.exceptions.ConnectionError as exception:
        print("==================================================", file=sys.stderr)
        print("GETCODE ERROR requests.exceptions.ConnectionError: " + str(exception), file=sys.stderr)
        print("==================================================", file=sys.stderr)

  fetchingThread = threading.Thread(name="Page-Parser", target=getcode, args=(arguments.keywords,))
  fetchingThread.start()

  for item in range(arguments.num_lines):
    text = codeQueue.get()
    print(text)
