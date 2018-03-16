from urllib.request import urlopen
import simplejson
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
        original_query = request.GET.get("q")
        query = original_query
        
        #searchDocument#########################################################################
        response=Search_View.searchDocument(query,filter_query,page,rows);
        document_found_count = response['response']['numFound']
        
        #spellcheck#########################################################################
        corrected = ''
        if(document_found_count<200 and len(original_query)>0):
            spellcheckreq = 'http://localhost:8983/solr/irproject/spell?spellcheck.q='+original_query.replace(' ','%20')+'&spellcheck=true&spellcheck.extendedResults=true&spellcheck.collate=true&wt=json'
            
            try:
                connection1 = urlopen(spellcheckreq)
                spellcheckedresult = simplejson.load(connection1)
                if(spellcheckedresult['spellcheck']['correctlySpelled'] == False):
                    if(len(spellcheckedresult['spellcheck']['collations'])>1):
                        corrected = spellcheckedresult['spellcheck']['collations'][1]['collationQuery']
                        preprocessor = preprocess.PreprocessPipeline()
                        #print(spellcheckedresult)
                        processed_query1 = preprocessor.process(original_query)
                        processed_query2 = preprocessor.process(corrected)
                        if(processed_query1==processed_query2):
                            corrected=''
            except:
                i=1
        
        #get documents of spellchecked query##############################################
        is_corrected_result = 0
        if(document_found_count==0):
            response=Search_View.searchDocument(corrected,filter_query,page,rows);
            document_found_count = response['response']['numFound']
            if(document_found_count>0):
                is_corrected_result = 1
        
        r = []
        for document in response['response']['docs']:
            url = Search_View.dir_path+document['id']
            data = json.load(open(url))
            data["id"]=document['id']
            r.append(data)
            
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
                pagination['links'].append({'index':'prev','link':(currentUrl+"&p="+str(p-1))});
            for i in range(minrange,maxrange):
                pagination['links'].append({'index':str(i),'link':(currentUrl+"&p="+str(i))});
            if not(p==maxpage):
                pagination['links'].append({'index':'next','link':(currentUrl+"&p="+str(p+1))});
        #######################################################
        
        return render(request, 'results.html',
        context={'query': original_query,'results': r,'spellcorrect': corrected,
        'document_found_count':document_found_count,'is_corrected_result':is_corrected_result,
        'filter_query':filter_query,'pagination':pagination})
    def searchDocument(query,filter_query,page,rows):
        #preprocess query
        preprocessor = preprocess.PreprocessPipeline()
        processed_query = preprocessor.process(query)
        if(len(processed_query)>0):
            #Boolean Or operator
            query = '+'.join(processed_query)    
        else:
            query = '*'
        fieldboost = []
        fieldboost.append('adviceMgmt_tag^1')
        fieldboost.append('company_name_tag^10')
        fieldboost.append('cons_tag^1')
        fieldboost.append('headquarter_tag^1')
        fieldboost.append('industry_tag^1')
        fieldboost.append('interview_details_tag^1')
        fieldboost.append('interview_question_tag^1')
        fieldboost.append('position_tag^1')
        fieldboost.append('pros_tag^1')
        fieldboost.append('review_description_tag^1')
        fieldboost.append('title_tag^1')
        fieldboost.append('competitors_tag^0.3')
        fieldboost = '+'.join(fieldboost)  
        
        params = []
        params.append('rows='+str(rows))
        params.append('defType=dismax')
        params.append('wt=json')
        params.append('qf='+fieldboost)
        params.append('start='+str((int(page)-1)*int(rows)))
        params.append('fq='+filter_query)
        params.append('q=+'+query)
        params.append('mm='+str(int((len(processed_query))*0.75)))
        url_params = '&'.join(params)    
        connection = urlopen('http://localhost:8983/solr/irproject/select?'+url_params)
        response = simplejson.load(connection)
        return response
        