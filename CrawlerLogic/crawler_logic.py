import requests
from CrawlerLogic.site_info import SiteInfo
from CrawlerLogic.link_factory import LinkFactory

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from queue import Queue, Empty
from threading import Thread, current_thread
import time
import re, os
from urllib import parse, robotparser
import math
import json, copy


class Crawler:
    def __init__(self, host):
        self.host = host

        self.host = self.host.replace("http://", "")
        self.host = self.host.replace("https://", "")
        if not self.host.endswith("/"):
            self.host = self.host + "/"

        self.word = None
        self.queue = Queue()
        self.toVisit = {}
        self.visited = {}
        self.pagesVisited = 0

        self.rp = robotparser.RobotFileParser()
        self.rp.set_url("http://%s" % self.host)
        self.rp.read()

    def crawl(self, root="", threads=5, maxPages=math.inf):
        self.linkFactory = LinkFactory(self.host)
        rootUrl = self.linkFactory.repairLink(root)
        self.queue.put([rootUrl, ""])
        self.maxPages = maxPages
        workers = []

        for i in range(threads):
            worker = Thread(target=self.parser)
            worker.start()
            workers.append(worker)
            if i==0:
                time.sleep(2.5)
        for worker in workers:
            worker.join()
        self._removeLinksWithoutNodes()


    def parser(self):
        try:
            while True:
                if self.pagesVisited >= self.maxPages:
                    return

                siteToVisitInfo = self.queue.get_nowait()
                url = siteToVisitInfo[0]
                site = SiteInfo(requests.get(url, headers={"Connection": "close"}))
                site.parent = siteToVisitInfo[1]
                #url = site.url
                if not site.status_code == 200:
                    continue
                self.visited[url] = site
                url = url.replace("https://", "http://")
                print ("Joined url: %s from thread: %s" % (url, current_thread().getName()))

                self.pagesVisited += 1

                for link in site.getLinks():
                    try:
                        link = self.linkFactory.repairLink(link)
                    except InvalidURLException:
                        continue
                    if self.host not in link:
                        continue

                    #self.visited[url].addChild(link)

                    if link not in self.toVisit and self.rp.can_fetch("*", link):
                        self.toVisit[link] = site
                        self.queue.put([link, url])

        except Empty:
            print ("kolejka byla pusta wiec przestalem istniec pozdrawiam %s" % current_thread().getName())

    def findWord(self, word):
        self.word = word

    def _removeLinksWithoutNodes(self):
        for (key, visitedSite) in self.visited.items():
            lista = copy.deepcopy(visitedSite.children)
            for site in lista:
                if site not in self.visited.keys():
                    visitedSite.children.remove(site)

    def generateGraphJsonToFileFromData(self):
        nodes = []
        edges = []
        min = 10000000
        for key, value in self.visited.items():
            if value.countChildren()<min:
                min = value.countChildren()
        for key, value in self.visited.items():
            node ={}
            node['data'] = {'id':key, 'concentric':(value.countChildren()-min)}
            nodes.append(node)

        for key, visitedSite in self.visited.items():
            """
            for child in visitedSite.children:
                edge = {}
                edge['data'] = {'source':key, 'target':child}
                edges.append(edge)
            """
            print(visitedSite.parent)
            edge = {}
            edge['data'] = {'source':visitedSite.parent, 'target':key}
            edges.append(edge)

        elements = {'nodes':nodes, 'edges':edges}
        elements = json.dumps(elements)
        url = self.host.rstrip("/")
        url = url.replace("http://", "").replace("https://", "")
        __location__ = os.path.realpath(
                        os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__ , "output/%s.json" % url), 'w+') as f:
            f.write(elements)



if __name__ == '__main__':
    url = 'http://www.facebook.com'

    crawlik = Crawler(url)
    crawlik.crawl("", 10, 75)
    crawlik.generateGraphJsonToFileFromData()

