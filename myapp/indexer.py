import pysolr
class Indexer:
    solr_url = 'http://127.0.0.1:8983/solr/irproject/'
    def __init__(self):
        self.solr = pysolr.Solr(Indexer.solr_url, timeout=10)
        return 
        
    '''
    solr.add([
        {
            "id": "doc_1",
            "title": "A test document",
        },
        {
            "id": "doc_2",
            "title": "The Banana: Tasty or Dangerous?",
            "_doc": [
                { "id": "child_doc_1", "title": "peel" },
                { "id": "child_doc_2", "title": "seed" },
            ]
        },
    ])
    '''
    
    def add(self,data):
        try:
            self.solr.add([data])
        except Exception as e:
            print(e)
            return 0
        return 1
    
    
    '''
    # Finally, you can delete either individual documents,
    solr.delete(id='doc_1')

    # also in batches...
    solr.delete(id=['doc_1', 'doc_2'])

    # ...or all documents.
    solr.delete(q='*:*')
    '''
    def delete(self,id):
        try:
            self.solr.delete(id)
        except Exception as e:
            print(str(e))
            return 0
        return 1
        
    def delete_all_index(self):
        try:
            self.solr.delete(q='*:*')
        except Exception as e:
            print(str(e))
            return 0
        return 1