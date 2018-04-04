from urllib.request import urlopen
from django.utils.http import urlquote
import simplejson
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from myapp.preprocess import preprocess
import myapp
import json
import os
import os.path
import re
import pysolr
# Create your views here.
class Search_View(TemplateView):
    dir_path =  os.path.dirname(myapp.__file__)+'\\..'
    def search(request, **kwargs):
        #get query and page parameters from request###################################################
        rows = request.GET.get("r")
        if(rows is None):
            rows= 10
        page = request.GET.get("p")
        if(page is None):
            page= "1"
        filter_query = request.GET.get("fq")
        if(filter_query is None):
            filter_query='*:*'
        filter_query_companyname = request.GET.get("companyname")
        if(filter_query_companyname is None):
            filter_query_companyname=''
        original_query = request.GET.get("q")
        query = original_query
        
        #searchDocument#########################################################################
        response=Search_View.searchDocument(query,filter_query,page,rows,filter_query_companyname);
        document_found_count = response['response']['numFound']
        facet_company = response['facet_counts']['facet_fields']["facet_text_en_nosplit"]
        index=len(facet_company)-1
        while(index>=0):
            if not(str(facet_company[index]).isdigit()):
                facet_company[index] = "("+str(facet_company[index+1])+") "+facet_company[index]
                if(facet_company[index+1]==0):
                    facet_company.pop(index+1);
                    facet_company.pop(index);
                else:
                    facet_company.pop(index+1);
            index=index-1
        
        doctype_count = [0,0,0]
        facet_type = response['facet_counts']['facet_fields']["doctype"]
        index=len(facet_type)-1
        while(index>=0):
            if not(str(facet_type[index]).isdigit()):
                if (facet_type[index].find('interview')>=0):
                    doctype_count[2]=doctype_count[2]+facet_type[index+1]
                if (facet_type[index].find('review')>=0):
                    doctype_count[1]=doctype_count[1]+facet_type[index+1]
                if (facet_type[index].find('company')>=0):
                    doctype_count[0]=doctype_count[0]+facet_type[index+1]
            index=index-1
        facet_type=[]
        if(doctype_count[0]>0):
            facet_type.append("("+str(doctype_count[0])+") Companies")
        if(doctype_count[1]>0):
            facet_type.append("("+str(doctype_count[1])+") Reviews")
        if(doctype_count[2]>0):
            facet_type.append("("+str(doctype_count[2])+") Interviews")
        if(len(facet_type)<=1):
            facet_type=[]
        
        facet_word = response['facet_counts']['facet_fields']["spellchecktext"]
        index=len(facet_word)-1
        while(index>=0):
            if not(str(facet_word[index]).isdigit()):
                if (facet_word[index+1]<50):
                    facet_word.pop(index+1);
                    facet_word.pop(index);
            index=index-1
      
        facet_word=' '.join([str(x) for x in facet_word])
        preprocessor = preprocess.PreprocessPipeline()
        facet_word = preprocessor.processWithoutStemming_remove_query(facet_word,query)
        if(len(facet_word)>15):
            facet_word = facet_word[:15]
        
        #spellcheck#########################################################################
        corrected = original_query
        if(document_found_count<200 and len(original_query)>0):
            spellcheckreq = 'http://localhost:8983/solr/irproject/spell?spellcheck.q='+original_query.replace(' ','%20')+'&spellcheck=true&fq='+filter_query+'&spellcheck.extendedResults=true&spellcheck.collate=true&wt=json'
            
            try:
                connection1 = urlopen(spellcheckreq)
                spellcheckedresult = simplejson.load(connection1)
                if(spellcheckedresult['spellcheck']['correctlySpelled'] == False):
                    if(len(spellcheckedresult['spellcheck']['collations'])>1):
                        corrected = spellcheckedresult['spellcheck']['collations'][1]['collationQuery']
                        #preprocessor = preprocess.PreprocessPipeline()
                        #processed_query1 = preprocessor.process(original_query)
                        #processed_query2 = preprocessor.process(corrected)
                        #if(processed_query1==processed_query2):
                        #    corrected=''

            except Exception as e: 
                print(e)
        
        #get documents of spellchecked query##############################################
        is_corrected_result = 0
        if(document_found_count==0):
            response=Search_View.searchDocument(corrected,filter_query,page,rows,filter_query_companyname);
            document_found_count = response['response']['numFound']
            if(document_found_count>0):
                is_corrected_result = 1
            
        
        ##Load oringal json files#######################################################
        all_words='';
        r = []
        for document in response['response']['docs']:
            try:
                url = Search_View.dir_path+document['id']
                with open(url, encoding='utf-8') as fh:
                    data = json.load(fh)
                data["id"]=document['id']
                data["doctype"]=document['doctype']
                if(data["company_name"][(len(data["company_name"])-11):] ==' Interviews' ):
                    data["company_name"] = data["company_name"][:(len(data["company_name"])-11)]
                if(data["company_name"][(len(data["company_name"])-8):] ==' Reviews' ):
                    data["company_name"] = data["company_name"][:(len(data["company_name"])-8)]
                    
                
                data["search_title"]=[];  
                if 'doctype' in data and not(data["doctype"][0] is None):
                    if not (data["doctype"][0].find('interview') == -1) :
                        data["search_title"].append("Interview");
                    if not (data["doctype"][0].find('review') == -1) :
                        data["search_title"].append("Review");
                    if not (data["doctype"][0] == 'company') :
                        url = Search_View.dir_path+"\\crawled_data\\company\\"+data["company_name"]+".json"
                        try:
                            company_data = json.load(open(url))
                            data["logo"] = company_data["logo"]
                        except:
                            i=1
                if 'title' in data and not(data["title"] is None):
                    data["search_title"].append(data["title"]);
                if 'company_name' in data and not(data["company_name"] is None):
                    data["search_title"].append(data["company_name"]);
                data["search_title"] = ' - '.join(data["search_title"])        
                
                data["search_description"]=[]; 
                if 'headquarter' in data and not(data["headquarter"] is None):
                    data["search_description"].append("Headquarter: "+data["headquarter"]);
                if 'size' in data and not(data["size"] is None):
                    data["search_description"].append("Size: "+data["size"]);
                if 'founded' in data and not(data["founded"] is None):
                    data["search_description"].append("Founded: "+data["founded"]);
                if 'industry' in data and not(data["industry"] is None):
                    data["search_description"].append("Industry: "+data["industry"]);
                if 'revenue' in data and not(data["revenue"] is None):
                    data["search_description"].append("Revenue: "+data["revenue"]);
                if 'competitors' in data and not(data["competitors"] is None):
                    data["search_description"].append("Competitors: "+data["competitors"]);
                    
                if 'location' in data and not(data["location"] is None):
                    data["search_description"].append("Location: "+data["location"]);
                if 'interview_details' in data and not(data["interview_details"] is None):
                    data["search_description"].append("Details: "+data["interview_details"]);
                if 'interview_question' in data and not(data["interview_question"] is None):
                    data["search_description"].append("Questions: "+data["interview_question"]);
                if 'result1' in data and not(data["result1"] is None):
                    data["search_description"].append(data["result1"]);
                if 'result2' in data and not(data["result2"] is None):
                    data["search_description"].append(data["result2"]);
                if 'result3' in data and not(data["result3"] is None):
                    data["search_description"].append(data["result3"]);
                 

                if 'pros' in data and not(data["pros"] is None):
                    data["search_description"].append("Pros: "+data["pros"]);
                if 'cons' in data and not(data["cons"] is None):
                    data["search_description"].append("Cons: "+data["cons"]);
                if 'adviceMgmt' in data and not(data["adviceMgmt"] is None):
                    data["search_description"].append("Advice to Management: "+data["adviceMgmt"]);
                if 'review_description' in data and not(data["review_description"] is None):
                    data["search_description"].append("Details: "+data["review_description"]);
                if 'opinion1' in data and not(data["opinion1"] is None):
                    data["search_description"].append(data["opinion1"]);
                if 'opinion2' in data and not(data["opinion2"] is None):
                    data["search_description"].append(data["opinion2"]);
                if 'opinion3' in data and not(data["opinion3"] is None):
                    data["search_description"].append(data["opinion3"]);
                data["search_description"] = ' '.join(data["search_description"])   
                
                
                all_words = all_words+data["search_description"] + " "
                all_words = all_words+data["search_title"] + " "
                
                if 'rating' in data and not(data["rating"] is None):
                    data["rating"] = float(data["rating"]);
                
                r.append(data) 
            
            except Exception as e: 
                print(e)    
        
        preprocessor = preprocess.PreprocessPipeline()
        #keys1 = query.split(" ") 
        keys1 = list(set(preprocessor.process(query)))
        keys2 = re.findall(r"[\w']+", all_words)
        t = []
        for key1 in keys1:
            t =  Search_View.getSyno(key1)
            if not(t is None):
                keys1 = keys1+t;
        keys2 = list(set(keys2))
        keys3 = []
        print(keys1)    
        for key1 in keys1:
            length = int(len(key1)*(-0.25));
            if length==0:
                length = -1
            processed_query1 = key1[:length]
            for key2 in keys2:
                if not(key2 in keys3):
                    if(key2.lower().find(processed_query1.lower())==0): 
                        processed_query2 = preprocessor.process(key2);
                        if(len(processed_query2)>0):
                            processed_query2=processed_query2[0]
                        else:    
                            processed_query2 = key2
                        print(key1+"=="+processed_query2)
                        if(key1==processed_query2): 
                            keys3.append(key2)
        keys3 = sorted(keys3, key=len)[::-1]       
        for doc in r:  
            try:          
                for key in keys3:    
                    doc["search_description"]=doc["search_description"].replace(key,'<span class="highlight">'+key+'</span>')
                    doc["search_title"]=doc["search_title"].replace(key,'<span class="title-highlight">'+key+'</span>')
               
            except Exception as e: 
                print(e)    
        
        ##pagination#######################################################
        minpage=0
        maxpage=0
        interval = 5
        p = int(page)
        pagination=None
        if document_found_count >0 :
            minpage =1
            maxpage = int(int(document_found_count)/int(rows))
            if not (document_found_count%rows == 0):
                maxpage = maxpage+1
            if p-interval>minpage:
                minrange = p-interval
            else:
                minrange= minpage
            if p+interval<maxpage:
                maxrange = p+interval
            else:
                maxrange= maxpage
            pagination = {'page':page,'minpage':minpage,'maxpage':maxpage}
            pagination['links']=[]
            currentUrl =request.get_full_path()
            currentUrl=currentUrl.replace('&p='+page,'')
            if not(p==minpage):
                pagination['links'].append(
                {'index':'prev','link':(currentUrl+"&p="+str(p-1))});
            for i in range(minrange,maxrange+1):
                pagination['links'].append({'index':str(i),'link':(currentUrl+"&p="+str(i))});
            if not(p==maxpage):
                pagination['links'].append({'index':'next','link':(currentUrl+"&p="+str(p+1))});
            if(len(pagination['links'])==1):
                pagination['links']=[]
        #######################################################
        
        return render(request, 'results.html',
        context={'query': original_query,'results': r,'spellcorrect': corrected,
        'document_found_count':document_found_count,'is_corrected_result':is_corrected_result,'filter_query_companyname':filter_query_companyname,
        'filter_query':filter_query,'pagination':pagination,'facet_company':facet_company,'facet_type':facet_type,'facet_word':facet_word})
    
    def getSyno(query):
        a=['firm', 'corpor', 'enterpris', 'compani', 'ventur']
        b=['competitor', 'rival', 'challeng', 'oppon', 'oppos', 'adversari', 'antagonist', 'combat', 'enemi', 'foe', 'competit', 'opposit']
        c=['job', 'post', 'appoint', 'role', 'occup', 'employ', 'duti', 'placement']
        d=['industri', 'busi', 'trade', 'field', 'line']
        e=['pro', 'strength', 'benefit', 'good']
        f=['con', 'weak', 'neg', 'disadvantag']
        g=['enjoy','pleas','pleasur','nice','agreeabl','satisfi','gratifi','best','good','fun','happi','great','awesom','amaz','incred','impress','wonder','spectacular','astonish','unbeliev','magnific','incred']
        h=['sad','disagre', 'irksom', 'troublesom', 'annoi', 'irrit', 'vexati', 'displeas', 'uncomfort', 'distress', 'nasti', 'horribl', 'appal', 'terribl', 'aw', 'dread', 'hate', 'detest', 'miser', 'abomin', 'execr', 'odiou', 'invidi', 'objection', 'offens', 'obnoxi', 'repugn', 'repuls', 'repel', 'revolt', 'disgust', 'distast', 'nauseat', 'unsavour']
        if(query in a):
            return a;
        if(query in b):
            return b;
        if(query in c):
            return c;
        if(query in d):
            return d;
        if(query in e):
            return e;
        if(query in f):
            return f;
        if(query in g):
            return g;
        if(query in h):
            return h;
        return None;
    
    def searchDocument(query,filter_query,page,rows,filter_query_companyname):
        if(len(query)>0):
            #preprocess query
            preprocessor = preprocess.PreprocessPipeline()
            processed_query = preprocessor.process(query)
            
            company_name_boost = 10
            competitors_boost = 0.3
            interview_boost = 1
            industry_boost = 1
            pros_boost = 1
            cons_boost = 1
            title_boost = 1
            position_boost = 6
            if(any(x in processed_query for x in ['competitor', 'rival', 'challeng', 'oppon', 'oppos', 'adversari', 'antagonist', 'combat', 'enemi', 'foe', 'competit', 'opposit'])):
                competitors_boost=3
            if(any(x in processed_query for x in ['industri', 'busi', 'trade', 'field', 'line'])):
                industry_boost=3
            if(any(x in processed_query for x in ['interview'])):
                interview_boost=5
            if(any(x in processed_query for x in ['pro', 'strength', 'benefit'])):
                pros_boost=3
            if(any(x in processed_query for x in ['con', 'weak', 'neg', 'disadvantag'])):
                cons_boost=3
           
            
            fieldboost = []
            if(len(processed_query)>0):
                #Boolean Or operator
                query = '+'.join(processed_query)     
                fieldboost.append('adviceMgmt_tag^1')
                fieldboost.append('company_name_tag^'+str(company_name_boost))
                fieldboost.append('cons_tag^'+str(cons_boost))
                fieldboost.append('headquarter_tag^1')
                fieldboost.append('industry_tag^'+str(industry_boost))
                fieldboost.append('interview_details_tag^'+str(interview_boost))
                fieldboost.append('interview_question_tag^'+str(interview_boost))
                fieldboost.append('position_tag^'+str(position_boost))
                fieldboost.append('pros_tag^'+str(pros_boost))
                fieldboost.append('review_description_tag^1')
                fieldboost.append('title_tag^'+str(title_boost))
                fieldboost.append('competitors_tag^'+str(competitors_boost))
            else:
                query = query.replace(' ','%20')
            fieldboost.append('adviceMgmt^1')
            fieldboost.append('company_name^'+str(company_name_boost))
            fieldboost.append('cons^'+str(cons_boost))
            
            fieldboost.append('headquarter^1')
            fieldboost.append('industry^'+str(industry_boost))
            fieldboost.append('interview_details^'+str(interview_boost))
            fieldboost.append('interview_question^'+str(interview_boost))
            fieldboost.append('position^'+str(position_boost))
            fieldboost.append('pros^'+str(pros_boost))
            fieldboost.append('review_description^1')
            fieldboost.append('title^'+str(title_boost))
            fieldboost.append('competitors^'+str(competitors_boost))
            fieldboost = '+'.join(fieldboost)  
                
            params = []
            params.append('rows='+str(rows))
            params.append('defType=dismax')
            params.append('wt=json')
            params.append('qf='+fieldboost)
            params.append('start='+str((int(page)-1)*int(rows)))
            params.append('fq='+filter_query)
            if(len(filter_query_companyname)>0):
                params.append('fq=facet_text_en_nosplit:"'+urlquote(filter_query_companyname)+'"')
            params.append('q=+'+query)
            params.append('mm='+str(int((len(processed_query))*0.75)))
        else:
            params = []
            params.append('rows='+str(rows))
            params.append('wt=json')
            params.append('start='+str((int(page)-1)*int(rows)))
            params.append('fq='+filter_query)
            if(len(filter_query_companyname)>0):
                params.append('fq=facet_text_en_nosplit:"'+urlquote(filter_query_companyname)+'"')
            params.append('q=*:*')
        url_params = '&'.join(params)    
        connection = urlopen('http://localhost:8983/solr/irproject/select?'+url_params+'&facet.field=facet_text_en_nosplit&facet.field=spellchecktext&facet.field=doctype&facet.query='+query+'&facet=on')
        response = simplejson.load(connection)
        return response
        