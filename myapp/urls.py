"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from myapp import views
from myapp import crawler
from myapp import indexing
urlpatterns = [

	url(r'^$', views.HomePageView.as_view()),
	url(r'^crawl$',  crawler.CrawlerView.crawler, name='crawl'),
	url(r'^crawl/start$',  crawler.CrawlerView.start_crawling, name='start_crawling'),
	url(r'^crawl/start/(?P<query>\w+)$',  crawler.CrawlerView.start_crawling, name='start_crawling'),
	url(r'^crawl/stop$',  crawler.CrawlerView.stop_crawling, name='stop_crawling'),
    
	url(r'^indexing$',  indexing.IndexingView.index, name='index'),
	url(r'^indexing/start$',  indexing.IndexingView.start_indexing, name='start_indexing'),
	url(r'^indexing/isindexing$',  indexing.IndexingView.is_indexing, name='is_indexing'),
	url(r'^indexing/stop$',  indexing.IndexingView.stop_indexing, name='stop_indexing'),
	url(r'^indexing/files$',  indexing.IndexingView.get_files, name='get_files'),
]
