#!/usr/bin/env python3

# To make this program executable from any process working directory, run:
# ln -s getcode.py ~/.local/bin/getcode

import argparse
import html.parser
import requests

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Download some code matching given keywords.')
  parser.add_argument('code_keywords', metavar='N', type=str, nargs='+', help='an integer for the accumulator')
  arguments = parser.parse_args()

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
        print("", flush=True)

    def handle_endtag(self, tag):
      if tag in ['code', 'td'] and self.isCode:
        self.isCode = False
        print("", flush=True)

    def handle_data(self, data):
      if self.isCode:
        data_lines = data.split("\n")
        for data_line in data_lines:
          print(data_line, flush=True)

  searchAddress = 'https://html.duckduckgo.com/html?q={}'.format("+".join(arguments.code_keywords))
  searchPageParser = SearchPageParser()
  searchPageParser.feed(requests.get(searchAddress, headers={'user-agent': 'getcode/0.0.1'}).text)

  print(f'Code for: {" ".join(arguments.code_keywords)}', flush=True)
  print("--------------------------------------------------", flush=True)
  print(searchAddress, flush=True)

  codePageParser = CodePageParser()
  for webAddress in searchPageParser.webAddresses:

    print("==================================================", flush=True)

    webAddressWithProtocol = "http://" + webAddress
    print(webAddressWithProtocol, flush=True)

    try:
      codePageParser.feed(requests.get(webAddressWithProtocol).text)
    except requests.exceptions.ConnectionError as exception:
      print("==================================================", flush=True)
      print("GETCODE ERROR requests.exceptions.ConnectionError: " + str(exception), flush=True)
      print("==================================================", flush=True)
