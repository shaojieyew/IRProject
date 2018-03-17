from django.shortcuts import render
from django.views.generic import TemplateView
from myapp.solr_manager import index_manager
from django.http import JsonResponse
# Create your views here.
class IndexingView(TemplateView):
    
    def index(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status})
    def start_indexing(request, **kwargs):
        type = request.GET.get("indexing_type")
        indexManager = index_manager.IndexManager()
        if(type == 'all'):
            indexManager.start_indexing()
        indexManager.start_indexing(type)
        #print(files)
        return render(request, 'indexing.html', context={'status': "done"})
    def is_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status})
    def stop_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        indexManager.stop_indexing()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status})
    def get_files(request, **kwargs):
        indexManager = index_manager.IndexManager()
        files = indexManager.get_non_indexed_file()
        #print(files)
        
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status,'files':files})
    
    def delete(request, **kwargs):  
        indexManager = index_manager.IndexManager()
        indexManager.delete_all_index()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return render(request, 'indexing.html', context={'status': status,'deleted': 1})
    def check_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        if(indexManager.is_indexing()==1):
            status = "indexing" 
        else:
            status = "" 
        return JsonResponse({'status':status})
        