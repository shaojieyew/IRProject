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
class CrawlerView(TemplateView):
    scraplist = []
    
    def crawler(request, **kwargs):
        crawling_file = Path("crawling.txt")
        is_crawling = 0
        if crawling_file.is_file():
            is_crawling = 1
        return render(request, 'crawler.html', context={'is_crawling': is_crawling})
      
    def start_crawling(request, **kwargs):
        #start crawling
        crawling_file = Path("crawling.txt")
        if not(crawling_file.is_file()):
            keyword = request.GET.get("crawl_keyword")
            keyword.strip()
            crawler = None
            if(request.GET.get("crawl_option")=='gdr'):
                crawler = 'glassdoor_company_review'
            if(request.GET.get("crawl_option")=='gdi'):
                crawler = 'glassdoor_company_interview'
            if(request.GET.get("crawl_option")=='idr'):
                crawler = 'indeed_company_review'
                
            if(len(keyword)>0):
                os.system("scrapy crawl "+crawler+" -a keyword="+keyword)
            else:
                os.system("scrapy crawl "+crawler)  
        
        
    def stop_crawling(request, **kwargs):
        #start crawling
        #os.system("scrapy crawl company_review")
        crawling_file = Path("crawling.txt")
        if crawling_file.is_file():
            os.remove("crawling.txt")
            
        crawling_file = Path("crawling.txt")
        is_crawling = 0
        if crawling_file.is_file():
            is_crawling = 1
        return render(request, 'crawler.html', context={'is_crawling': is_crawling})
        
    