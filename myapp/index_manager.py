
import json
import os
import myapp
import os.path
from django.conf import settings
from pathlib import Path
import re

class IndexManager:
    def __init__(self):
        return 

    def get_non_indexed_file(self):
    
        dir_path =  os.path.join( getattr(settings, "PROJECT_ROOT", None), '..')

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
        
        
    
    def start_indexing(self):
        dir_path =  os.path.join( getattr(settings, "PROJECT_ROOT", None), '..')

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
        
        for folder in folders:
            search_dir = dir_path + '\\crawled_data\\'+folder
            os.chdir(search_dir)
            files = filter(os.path.isfile, os.listdir(search_dir))
            files = filter(lambda x: os.path.getmtime(x) > last_indexed[folder], files)
            files = [os.path.join(search_dir, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            for file in files:
                print(file)
                last_indexed[folder] = os.path.getmtime(file)
                with open(last_indexed_timestamp_file, 'w') as file:
                    file.write(json.dumps(last_indexed)) 
        
        return "finished"
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