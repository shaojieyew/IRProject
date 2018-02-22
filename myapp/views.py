from django.shortcuts import render
from django.views.generic import TemplateView
import twitter
import subprocess
import requests, base64
import oauth2 as oauth2
from twisted.internet import reactor
import json
import time
import pysolr,json,argparse
import os
from pathlib import Path
from myapp import tweet_api
# Create your views here.
class HomePageView(TemplateView):
    scraplist = []
    
    def get(self,request, **kwargs):
        #start crawling
        #os.system("scrapy crawl company_review")
        return render(request, 'index.html', context={'body': kwargs})