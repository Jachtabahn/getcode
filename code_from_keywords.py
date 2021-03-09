from html.parser import HTMLParser
import requests
import sys

isResult = False
isCode = False

webAddresses = []

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        global isResult
        if tag == 'a':
            if ('class', 'result__url') in attrs:
                isResult = True

    def handle_endtag(self, tag):
        global isResult
        if tag == 'a':
            isResult = False

    def handle_data(self, data):
        global isResult
        if isResult:
            webAddresses.append(data.strip())

searchAddress = 'https://html.duckduckgo.com/html?q={}'.format("+".join(sys.argv[1:]))
r = requests.get(searchAddress, headers={'user-agent': 'code_from_keywords/0.0.1'})
parser = MyHTMLParser()
parser.feed(r.text)

print("--------------------------------------------------")
print(searchAddress)

for webAddress in webAddresses:

    print("==================================================")
    print(webAddress)

    class MySecondHTMLParser(HTMLParser):

        def handle_starttag(self, tag, attrs):
            global isCode
            if tag == 'code':
                isCode = True

        def handle_endtag(self, tag):
            global isCode
            if tag == 'code':
                isCode = False

        def handle_data(self, data):
            global isCode
            if isCode:
                print(data)

    r = requests.get("https://" + webAddress)
    parser = MySecondHTMLParser()
    parser.feed(r.text)
