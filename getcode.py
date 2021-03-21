#!/usr/bin/env python3

# To make this program executable from any process working directory, run:
# ln -s ~/Software/getcode/getcode.py ~/.local/bin/getcode

import argparse
import html.parser
import requests
import sys

parser = argparse.ArgumentParser(description='Download some code matching given keywords.')

parser.add_argument('--num-tags', type=int, default=15, help='of at least how many tag nodes the content should be output (default: 15 tag nodes)')
parser.add_argument('keywords', metavar='N', type=str, nargs='+', help='an integer for the accumulator')

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
    numOutputTags = 0

    def handle_starttag(self, tag, attrs):
        if tag in ['code']:
            self.isCode = True
        if tag == 'td':
            attrsDict = dict(attrs)
            classString = attrsDict['class']
            words = classString.split(' ')
            if 'blob-code' in words:
                self.isCode = True

    def handle_endtag(self, tag):
        if tag in ['code', 'td'] and self.isCode:
            self.isCode = False
            print()

    def handle_data(self, data):
        if self.isCode:
            print(data, end="")
            self.numOutputTags += 1
        if self.numOutputTags >= arguments.num_tags:
            exit()


searchAddress = 'https://html.duckduckgo.com/html?q={}'.format("+".join(arguments.keywords))
searchPageParser = SearchPageParser()
searchPageParser.feed(requests.get(searchAddress, headers={'user-agent': 'code_from_keywords/0.0.1'}).text)

print("--------------------------------------------------")
print(searchAddress)

codePageParser = CodePageParser()
for webAddress in searchPageParser.webAddresses:

    print("==================================================")
    print(webAddress)

    codePageParser.feed(requests.get("https://" + webAddress).text)
