from dateutil import parser
import json
import myapp
import os
import datetime
import os.path
from django.conf import settings
from pathlib import Path
import re
from myapp.preprocess import preprocess
from myapp.solr_manager import indexer as solrIndexer 

class IndexManager:
    def __init__(self):
        return 
    
    def get_non_indexed_file(self):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'
        folders = ['glassdoor_company','glassdoor_interview','glassdoor_review','indeed_company','indeed_review']
        last_indexed = {'glassdoor_company':0,'glassdoor_interview':0,'glassdoor_review':0,'indeed_company':0,'indeed_review':0}
        last_indexed_timestamp_file = dir_path+'\\crawled_data\\last_indexed.txt'
        
        my_file = Path(last_indexed_timestamp_file)
        if not(my_file.is_file()):
            open(last_indexed_timestamp_file, 'w').close()   
            with open(last_indexed_timestamp_file, 'w') as file:
                file.write(json.dumps(last_indexed)) 
        with open(last_indexed_timestamp_file) as handle:
            last_indexed = json.loads(handle.read())
        all_files = []
        for folder in folders:
            search_dir = dir_path + '\\crawled_data\\'+folder
            os.chdir(search_dir)
            files = filter(os.path.isfile, os.listdir(search_dir))
            files = filter(lambda x: os.path.getmtime(x) > last_indexed[folder] , files)
            files = [os.path.join(search_dir, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            all_files=all_files+files
        return all_files
        
    
    def is_indexing(self):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'
        indicate_indexing_file = dir_path+'\\crawled_data\\indexing.txt'
        my_file = Path(indicate_indexing_file)
        if (my_file.is_file()):
            return 1
        else:
            return 0
            
    def stop_indexing(self):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'
        indicate_indexing_file = dir_path+'\\crawled_data\\indexing.txt'
        my_file = Path(indicate_indexing_file)
        print(indicate_indexing_file)
        if (my_file.is_file()):
            os.remove(indicate_indexing_file)
            
        
            
    def start_indexing(self):
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'
        indicate_indexing_file = dir_path+'\\crawled_data\\indexing.txt'
        folders = ['glassdoor_company','glassdoor_interview','glassdoor_review','indeed_company','indeed_review']
        last_indexed = {'glassdoor_company':0,'glassdoor_interview':0,'glassdoor_review':0,'indeed_company':0,'indeed_review':0}
        last_indexed_timestamp_file = dir_path+'\\crawled_data\\last_indexed.txt'
        
        open(indicate_indexing_file, 'w').close() 
        my_file = Path(last_indexed_timestamp_file)
        if not(my_file.is_file()):
            open(last_indexed_timestamp_file, 'w').close()   
            with open(last_indexed_timestamp_file, 'w') as file:
                file.write(json.dumps(last_indexed)) 
        with open(last_indexed_timestamp_file) as handle:
            last_indexed = json.loads(handle.read())
        
        preprocessor = preprocess.PreprocessPipeline()
        terminate = 0
        for folder in folders:
            search_dir = dir_path + '\\crawled_data\\'+folder
            os.chdir(search_dir)
            files = filter(os.path.isfile, os.listdir(search_dir))
            files = filter(lambda x: os.path.getmtime(x) > last_indexed[folder], files)
            files = [os.path.join(search_dir, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            print(search_dir)
            for file in files:
                if (Path(indicate_indexing_file).is_file()):
                    #print(file)
                    self.process_file(file,preprocessor)
                    last_indexed[folder] = os.path.getmtime(file)
                else:
                    terminate=1
                    print(search_dir)
                    break
            if terminate == 1:
                break
        with open(last_indexed_timestamp_file, 'w') as file:
            file.write(json.dumps(last_indexed))
        preprocessor.close()
        return "finished"
        
    def delete_all_index(self):
        index = solrIndexer.Indexer()
        index.delete_all_index()
        dir_path =  os.path.dirname(myapp.__file__)+'\\..'
        file = dir_path+'\\crawled_data\\last_indexed.txt'
        my_file = Path(file)
        if (my_file.is_file()):
            os.remove(file)
        return 
        
    def process_file(self,file,preprocessor):
        filename = file
        data = json.load(open(filename))
        data["id"]=filename.split('\\..')[1]
        data["doctype"]=filename.split('\\..')[1].replace("\\crawled_data\\", "").split('\\')[0]
        
        if not (data['company_name'] is None):
            if(data['company_name'][(len(data['company_name'])-11):] ==' Interviews' ):
                data['company_name'] = data['company_name'][:(len(data['company_name'])-11)]
            if(data['company_name'][(len(data['company_name'])-8):] ==' Reviews' ):
                data['company_name'] = data['company_name'][:(len(data['company_name'])-8)]
        try:
            if not (data['datetime'] is None):
                data['datetime'] = parser.parse(data['datetime'])
        except KeyError:
            i=1
        field_to_search=["company_name","headquarter","competitors","title","industry","position","pros","cons","adviceMgmt","review_description","interview_details","interview_question"]
        for field in field_to_search:
            try:
                if not (data[field] is None):
                    if (data[field].strip().lower() == 'unknown'):
                        data[field]=""
                    result = preprocessor.process(data[field])
                    if len(result)>0 :
                        data[field+"_tag"]=(' '.join(result)) 
            except KeyError:
                i=1
                #print("no key")
        #print(data["search_field"])
        index = solrIndexer.Indexer()
        result = index.add(data)
        
        #print(data);
        if result == 1: 
            print("company : "+data["company_name"])
            print("index added: "+data["id"])
        
        return 
    '''
    #filename = 'test.json'
    #data = json.load(open(filename))
    #Test preprocess
    #sentence = data["pros"]
    sentence = "In order to succeed at Accenture, you must be willing to put in a lot of hours for a number of years. On many projects there is an unwritten assumption that the company owns your time well beyond the 40 hours a week that they are paying you for. There are two types of people who generally succeed at Accenture. Most are highly task-oriented, type-A personalities who derive job satisfaction from creating a list of objectives, and completing them one by one. Very few people in this industry (and particularly at Accenture) are actually passionate about the subject matter of the work or the client who they do the work for. The second type of succesful person at Accenture is the \"salesman\" or \"saleswoman\". This is someone who has worked hard enough to get to a level where they can put together proposals and sell work (senior executive). They are excellent at \"schmoozing\" the client, and getting work sold. If you are not one of these two types, you should look elsewhere for employment. Finally, Accenture is the ultimate \"kiss-ass\" or \"brown-nose\" culture. Upon walking through the front door, you will find yourself surrounded by people who spent the majority of their primary school years sitting in the front row of the class, smiling at the teacher, asking more questions than necessary, and who were always the first to place a shiny red apple on the teacher's desk."
    sentence = "run ran"
    print (sentence)
    preprocessor = preprocess.PreprocessPipeline()
    sentence = preprocessor.process(sentence)
    preprocessor.close()
    print (sentence)
    '''
    
    #document indexing manager
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folders = ['\\crawled_data\\glassdoor_company','\\crawled_data\\glassdoor_interview','\\crawled_data\\glassdoor_review','\\crawled_data\\indeed_company','\\crawled_data\\indeed_review']
    last_indexed = {'glassdoor_company':0,'glassdoor_interview':0,'glassdoor_review':0,'indeed_company':0,'indeed_review':0}
    last_indexed_timestamp_file = dir_path+'\\crawled_data\\last_indexed.txt'
    
    my_file = Path(last_indexed_timestamp_file)
    if not(my_file.is_file()):
        open(last_indexed_timestamp_file, 'w').close()   
        with open(last_indexed_timestamp_file, 'w') as file:
            file.write(json.dumps(last_indexed)) 
    with open(last_indexed_timestamp_file) as handle:
        last_indexed = json.loads(handle.read())
    
    for folder in folders:
        search_dir = dir_path + folder
        os.chdir(search_dir)
        files = filter(os.path.isfile, os.listdir(search_dir))
        files = filter(lambda x: os.path.getmtime(x) > last_indexed[folder], files)
        files = [os.path.join(search_dir, f) for f in files]
        files.sort(key=lambda x: os.path.getmtime(x))
        for file in files:
            print(file)
            last_indexed[folder] = os.path.getmtime(file)
        print("======folder=======")
    
    with open(last_indexed_timestamp_file, 'w') as file:
        file.write(json.dumps(last_indexed)) 
    ''' 
    
    
    #preprocessing & Indexing
    '''
    filename = 'test.json'
    data = json.load(open(filename))
    data["id"]=filename
    preprocessor = preprocess.PreprocessPipeline()
    field_to_search=["title","position","pros","cons","adviceMgmt","review_description","opinion1","opinion2","opinion3"]
    data["search_field"] =[]
    for field in field_to_search:
        if not (data[field] is None):
            result = preprocessor.process(data[field])
            if len(result)>0 :
                data["search_field"]=data["search_field"] + result

    index = solrIndexer.Indexer()
    result = index.add(data)
    if result == 1:
        print("index added: "+data["id"])
    #print ('Part of Speech:', nlp.pos_tag(sentence))
    #print ('Named Entities:', nlp.ner(sentence))
    #print ('Constituency Parsing:', nlp.parse(sentence))
    #print ('Dependency Parsing:', nlp.dependency_parse(sentence)) 
    '''
    
    #querying
    '''
    query = "best"
    preprocessor = preprocess.PreprocessPipeline()
    queryTerms = preprocessor.process(query)
    
    searcher = solrSearcher.Searcher();
    search_result = searcher.search(queryTerms[0])
    print(search_result)
    '''