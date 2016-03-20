from django.shortcuts import render
from .forms import UrlForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import Http404
import os.path
from CrawlerLogic.crawler_logic import *
from threading import Thread
import requests
# Create your views here.

def home(request):
	
	def crawlWorker():
		c = Crawler(url)
		if 'shallow' in request.POST:
			c.crawl(threads=20, maxPages=18)
		elif 'deep' in request.POST:
			c.crawl(threads=25, maxPages=150)
		c.generateGraphJsonToFileFromData()
	
	if request.method == 'POST':
		form = UrlForm(request.POST)
		
		if form.is_valid():
			url = form.cleaned_data.get('url')
			
			try:
				requests.get(url)
			except requests.ConnectionError:
				return render(request, 'bug.html', {})

			url = url.replace("http://", "").replace("https://", "")
			url = url.rstrip("/")
			context = {
				'url': url,
			}
			worker = Thread(target=crawlWorker)
			worker.start()
			return render(request, 'map.html', context)
	
	else:
		form = UrlForm()
	context = {
		'form': form,
	}
	
	return render(request, 'home.html', context)

def url_page(request, url=None):
	fname = 'CrawlerLogic/output/%s.json' % url
	__location__ = os.path.realpath(
                        os.path.join(os.getcwd(), os.path.dirname(__file__)))
	if os.path.isfile(os.path.join(__location__, "..", fname)):
		f = open(os.path.join(__location__, "..", fname))
		return HttpResponse(f.read())
	else:
		raise Http404()
