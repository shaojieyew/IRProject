from django.shortcuts import render
from django.views.generic import TemplateView
from myapp.solr_manager import index_manager
from django.http import JsonResponse
from urllib.request import urlopen
import simplejson
# Create your views here.
class IndexingView(TemplateView):
    
    def getIndexCount():
        url='http://localhost:8983/solr/irproject/select?facet.field=doctype&facet.query=doctype&facet=on&fl=id&indent=on&q=*:*&wt=json'
        connection1 = urlopen(url)
        resp = simplejson.load(connection1)
        types={"Total Indexed Document":resp["response"]["numFound"]}
        facet_type = resp["facet_counts"]["facet_fields"]["doctype"]
        index=len(facet_type)-1
        while(index>=0):
            if not(str(facet_type[index]).isdigit()):
                types[str(facet_type[index])] = facet_type[index+1]
            index=index-1
        return types
        
    def index(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status, 'stats': IndexingView.getIndexCount()})
    def start_indexing(request, **kwargs):
        type = request.GET.get("indexing_type")
        indexManager = index_manager.IndexManager()
        if(type == 'all'):
            indexManager.start_indexing()
        indexManager.start_indexing(type)
        #print(files)
        return render(request, 'indexing.html', context={'status': "done", 'stats': IndexingView.getIndexCount()})
    def is_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status, 'stats': IndexingView.getIndexCount()})
    def stop_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        indexManager.stop_indexing()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status, 'stats': IndexingView.getIndexCount()})
    def get_files(request, **kwargs):
        indexManager = index_manager.IndexManager()
        files = indexManager.get_non_indexed_file()
        #print(files)
        
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status,'files':files, 'stats': IndexingView.getIndexCount()})
    
    def delete(request, **kwargs):  
        indexManager = index_manager.IndexManager()
        indexManager.delete_all_index()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status,'deleted': 1, 'stats': IndexingView.getIndexCount()})
    def check_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return JsonResponse({'status':status})
        