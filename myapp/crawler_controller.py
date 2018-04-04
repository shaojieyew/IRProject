from django.shortcuts import render
from django.views.generic import TemplateView
import twitter
import subprocess
import myapp
import requests, base64
import oauth2 as oauth2
from twisted.internet import reactor
import json
import time
import pysolr,json,argparse
import os
from pathlib import Path
from myapp import tweet_api
from django.http import JsonResponse
# Create your views here.
class CrawlerView(TemplateView):
    scraplist = []
    
    def crawler(request, **kwargs):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'+"\\crawling.txt"
        crawling_file = Path(dir_path)
        is_crawling = 0
        if crawling_file.is_file():
            is_crawling = 1
        return render(request, 'crawler.html', context={'is_crawling': is_crawling})
      
    def start_crawling(request, **kwargs):
        #start crawling
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'+"\\crawling.txt"
        crawling_file = Path(dir_path)
        if not(crawling_file.is_file()):
            open(dir_path, 'w').close()
            keyword = request.GET.get("crawl_keyword")
            keyword.strip()
            crawler = None
            if(request.GET.get("crawl_option")=='gdr'):
                crawler = 'glassdoor_company_review'
            if(request.GET.get("crawl_option")=='gdi'):
                crawler = 'glassdoor_company_interview'
            if(request.GET.get("crawl_option")=='idr'):
                crawler = 'indeed_company_review'
                
            os.chdir(os.path.dirname(myapp.__file__)+'\\..')
            if(len(keyword)>0):
                os.system("scrapy crawl "+crawler+" -a keyword="+keyword.replace(' ','_'))
            else:
                os.system("scrapy crawl "+crawler)  
        
        
    def stop_crawling(request, **kwargs):
        #start crawling
        #os.system("scrapy crawl company_review")
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'+"\\crawling.txt"
        crawling_file = Path(dir_path)
        if crawling_file.is_file():
            os.remove(dir_path)
            
        is_crawling = 0
        if crawling_file.is_file():
            is_crawling = 1
        return render(request, 'crawler.html', context={'is_crawling': is_crawling})
        
    def check_crawling(request, **kwargs):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'+"\\crawling.txt"
        crawling_file = Path(dir_path)
        is_crawling = 0
        if crawling_file.is_file():
            is_crawling = 1
        return JsonResponse({'is_crawling':is_crawling})
        
    