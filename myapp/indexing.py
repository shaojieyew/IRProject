from django.shortcuts import render
from django.views.generic import TemplateView
from myapp import index_manager
# Create your views here.
class IndexingView(TemplateView):
    
    def index(request, **kwargs):
        #indexManager = index_manager.IndexManager()
        #files = indexManager.get_non_indexed_file()
        #print(files)
        return render(request, 'indexing.html', context={'status': ""})
    def start_indexing(request, **kwargs):
        indexManager = index_manager.IndexManager()
        indexManager.start_indexing()
        #print(files)
        return render(request, 'indexing.html', context={'status': "done"})
      
    