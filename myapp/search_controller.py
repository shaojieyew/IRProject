from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from myapp.preprocess import preprocess
import myapp
import json
import os
import os.path
import pysolr
# Create your views here.
class Search_View(TemplateView):
    dir_path =  os.path.dirname(myapp.__file__)+'\\..'
    def search(request, **kwargs):
        original_query = request.GET.get("q")
        preprocessor = preprocess.PreprocessPipeline()
        processed_query = preprocessor.process(original_query)
        
        query = original_query
        if(len(processed_query)>0):
            query = processed_query[0]
            
        solr_url = settings.SOLR_URL
        solr = pysolr.Solr(solr_url, timeout=10)
        results = solr.search(query)
        r = []
        for result in results:
            url = Search_View.dir_path+result['id']
            data = json.load(open(url))
            data["id"]=result['id']
            r.append(data)
        return render(request, 'results.html', context={'query': original_query,'results': r})
