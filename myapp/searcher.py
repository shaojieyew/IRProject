import pysolr
from django.conf import settings
class Searcher:
    solr_url = settings.SOLR_URL
    def __init__(self):
        self.solr = pysolr.Solr(Searcher.solr_url, timeout=10)
        return 
    
    '''
    # Later, searching is easy. In the simple case, just a plain Lucene-style
    # query is fine.
    results = solr.search('bananas')

    # The ``Results`` object stores total results found, by default the top
    # ten most relevant results and any additional data like
    # facets/highlighting/spelling/etc.
    print("Saw {0} result(s).".format(len(results)))

    # Just loop over it to access the results.
    for result in results:
        print("The title is '{0}'.".format(result['title']))

    # For a more advanced query, say involving highlighting, you can pass
    # additional options to Solr.
    results = solr.search('bananas', **{
        'hl': 'true',
        'hl.fragsize': 10,
    })

    # You can also perform More Like This searches, if your Solr is configured
    # correctly.
    similar = solr.more_like_this(q='id:doc_2', mltfl='text')
    '''
    
    def search(self,data):
        try:
            results = self.solr.search(data)
            for result in results:
                print("The title is '{0}'.".format(result['title']))
            return results
        except:
            return None
    