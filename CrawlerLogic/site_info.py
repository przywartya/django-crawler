from bs4 import BeautifulSoup, SoupStrainer
from requests import Response

class SiteInfo(Response):
    def __init__(self, response, parent=None):
        self.__dict__ = response.__dict__

        self.parent = parent
        self.children = []

    def getLinks(self):
        linkers = SoupStrainer('a', href=True)
        return [link.get('href') for link in BeautifulSoup(self.content, "lxml", parse_only=linkers).find_all('a')]

    def countChildren(self):
        return len(self.children)

    def addChild(self, child):
        if child not in self.children:
            self.children.append(child)

    def setParent(self, parent):
        self.parent = parent
