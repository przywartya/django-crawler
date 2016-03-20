import re

class InvalidURLException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class LinkFactory:
    def __init__(self, host):
        self.host = host
        self.host = self.host.replace("http://", "")
        self.host = self.host.replace("https://", "")
        #self.regex = open('diago_perini').readline()
        self.regex = ".*" #TODO ZROBIĆ TEGO REGEXA ELO


    def repairLink(self, url):
        url = url.strip("/")
        url = self.replaceTripleSlashes(url)
        if not (url.startswith("http://") or url.startswith("https://")):
            if self.host in url:
                url = self.addHttpToLink(url)
            else:
                url = self.addHostToLink(url)
                url = self.addHttpToLink(url)
        url = self.removeHashSections(url)
        #url = self.removeParamsSections(url)
        url = self.replaceTripleSlashes(url)
        return self.validate(url)

    def addHostToLink(self, url):
        return '%s%s' % (self.host, url)

    def addHttpToLink(self, url):
        return 'http://%s' % url

    def removeHashSections(self, url):
        if "#" in url:
            return "".join(url.split("#")[:-1])
        else:
            return url

    def removeParamsSections(self, url):
        if "?" in url:
            return "".join(url.split("?")[:-1])
        else:
            return url

    def replaceTripleSlashes(self, url):
        return url.replace("///", "//")

    def validate(self, url):
        if re.match(self.regex, url):
            return url
        else:
            raise InvalidURLException