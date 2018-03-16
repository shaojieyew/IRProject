import scrapy
from scrapy.selector import Selector
from pathlib import Path
from scrapy.crawler import CrawlerProcess
import time
import json
import os

class GlassdoorSpider(scrapy.Spider):
    name = "glassdoor_company_interview"
    def start_requests(self):  
        o_url ='https://www.glassdoor.com/Reviews/singapore-reviews-SRCH_IL.0,9_IM1123_IP1.htm'
        if hasattr(self, 'keyword'):
            if not (self.keyword is None) and len(self.keyword)>0:
                keyword = self.keyword
                keywordLen = len(self.keyword)
                o_url ='https://www.glassdoor.com/Reviews/singapore-'+keyword+'-reviews-SRCH_IL.0,9_IM1123_KE10,'+str(keywordLen+10)+'_IP1.htm'
        
        

        url = self.peek_url()
        if not (url is None):
            url_arr = url.split(" ")
            if(url_arr[0]=='1'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
            if(url_arr[0]=='2'):  
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
            if(url_arr[0]=='3'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_interview)
        else:   
            fields=['company_name','datetime','title','link','rating','position','pros','cons','adviceMgmt','review_description','opinion1','opinion2','opinion3']
            
            my_file = Path('crawling.txt')
            if not(my_file.is_file()):
                open('crawling.txt', 'w').close()
            yield scrapy.Request(url=o_url, callback=self.parse_companies_list)

    
    def pop_url(self):
        my_list=[]
        my_file = Path('crawling.txt')
        if not(my_file.is_file()):
            return
        with open('crawling.txt', 'r') as f:
            my_list = [line.rstrip('\n') for line in f]
        if(len(my_list)==0):
            return None
        url = my_list.pop()
        open('crawling.txt', 'w').close()
        with open('crawling.txt', 'w') as f:
            for s in my_list:
                f.write(s + '\n')
        return url
    def peek_url(self):
        my_list=[]
        my_file = Path('crawling.txt')
        if not(my_file.is_file()):
            return
        with open('crawling.txt', 'r') as f:
            my_list = [line.rstrip('\n') for line in f]
        if(len(my_list)>0):
            url = my_list[-1]
            return url
        return None
        
    def push_url(self,url):
        my_list=[]
        my_file = Path('crawling.txt')
        if not (my_file.is_file()):
            return
        with open('crawling.txt', 'r') as f:
            my_list = [line.rstrip('\n') for line in f]
        my_list.append(url)
        open('crawling.txt', 'w').close()
        with open('crawling.txt', 'w') as f:
            for s in my_list:
                f.write(s + '\n')
    

            
        
    def parse_companies_list(self, response):
        if response.css('title::text').extract_first().find('Working at') == -1:
            list_of_company_url = []
            for quote in response.css('div.margBotXs'):
                company_name = quote.css('a.tightAll::text').extract_first()
                if(company_name[(len(company_name)-11):] ==' Interviews' ):
                    company_name = company_name[:(len(company_name)-11)]
                href =  quote.css('a.tightAll::attr(href)').extract_first()
                url = ('https://www.glassdoor.com'+href)
                list_of_company_url.append(url)
            next_url = response.css('li.next').css('a::attr(href)').extract_first()
            
            url = self.pop_url()
            
            if not (next_url is None):
                next_url = 'https://www.glassdoor.com'+next_url
                self.push_url('1 '+next_url)
            for coy_url in list_of_company_url:
                self.push_url('2 '+coy_url)
            
            url = self.peek_url()
            if not (url is None):
                url_arr = url.split(" ")
                if(url_arr[0]=='1'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
                if(url_arr[0]=='2'):  
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
                if(url_arr[0]=='3'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_interview)
            else:
                os.remove("crawling.txt")
        else:
            company_name = response.css('div.header.cell.info').css('h1.strong.tightAll::text').extract_first().strip()
            logo = response.css('span.sqLogo.tighten.lgSqLogo.logoOverlay').css('img::attr(src)').extract_first()
            video = response.css('div.featured-video::attr(data-video-url)').extract_first()
            website = response.xpath('//div[@class=\'infoEntity\']//a[@class=\'link\']/text()').extract_first()
            headquarter = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Headquarters\']/span[@class=\'value\']/text()').extract_first()
            size = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Size\']/span[@class=\'value\']/text()').extract_first()
            founded = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Founded\']/span[@class=\'value\']/text()').extract_first()
            type = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Type\']/span[@class=\'value\']/text()').extract_first()
            industry = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Industry\']/span[@class=\'value\']/text()').extract_first()
            revenue = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Revenue\']/span[@class=\'value\']/text()').extract_first()
            competitors = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Competitors\']/span[@class=\'value\']/text()').extract_first()
            if(company_name[(len(company_name)-11):] ==' Interviews' ):
                company_name = company_name[:(len(company_name)-11)]
            data = {'company_name':company_name,'logo':logo,'video':video,'website':website,'headquarter':headquarter,'size':size,
            'founded':founded,'type':type,'industry':industry,'revenue':revenue,'competitors':competitors}
                
      
            fileLocation = 'crawled_data/glassdoor_company'
            if not os.path.exists(fileLocation):
                os.makedirs(fileLocation)    
            file = open(fileLocation+'/'+company_name+'.json', 'w')
            json.dump(data, file)
            file.close()
            
            interview_url = response.css('a.interviews::attr(href)').extract_first()
            interview_url = 'https://www.glassdoor.com'+interview_url
            url = self.pop_url()
            self.push_url('3 '+interview_url)
            url = self.peek_url()
            if not (url is None):
                url_arr = url.split(" ")
                if(url_arr[0]=='1'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
                if(url_arr[0]=='2'):  
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
                if(url_arr[0]=='3'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_interview)
            else:
                os.remove("crawling.txt")
    def parse_company_detail(self, response):
        company_name = response.css('div.header.cell.info').css('h1.strong.tightAll::text').extract_first().strip()
        logo = response.css('span.sqLogo.tighten.lgSqLogo.logoOverlay').css('img::attr(src)').extract_first()
        video = response.css('div.featured-video::attr(data-video-url)').extract_first()
        website = response.xpath('//div[@class=\'infoEntity\']//a[@class=\'link\']/text()').extract_first()
        headquarter = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Headquarters\']/span[@class=\'value\']/text()').extract_first()
        size = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Size\']/span[@class=\'value\']/text()').extract_first()
        founded = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Founded\']/span[@class=\'value\']/text()').extract_first()
        type = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Type\']/span[@class=\'value\']/text()').extract_first()
        industry = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Industry\']/span[@class=\'value\']/text()').extract_first()
        revenue = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Revenue\']/span[@class=\'value\']/text()').extract_first()
        competitors = response.xpath('//div[@class=\'infoEntity\' and label/text()[1]=\'Competitors\']/span[@class=\'value\']/text()').extract_first()
        if(company_name[(len(company_name)-11):] ==' Interviews' ):
            company_name = company_name[:(len(company_name)-11)]
        data = {'company_name':company_name,'logo':logo,'video':video,'website':website,'headquarter':headquarter,'size':size,
        'founded':founded,'type':type,'industry':industry,'revenue':revenue,'competitors':competitors}
            
        fileLocation = 'crawled_data/glassdoor_company'
        if not os.path.exists(fileLocation):
            os.makedirs(fileLocation)    
        file = open(fileLocation+'/'+company_name+'.json', 'w')
        json.dump(data, file)
        file.close()
        
        interview_url = response.css('a.interviews::attr(href)').extract_first()
        interview_url = 'https://www.glassdoor.com'+interview_url
        url = self.pop_url()
        self.push_url('3 '+interview_url)
        url = self.peek_url()
        if not (url is None):
            url_arr = url.split(" ")
            if(url_arr[0]=='1'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
            if(url_arr[0]=='2'):  
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
            if(url_arr[0]=='3'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_interview)
        else:
            os.remove("crawling.txt")
        #interview_url = response.css('a.interviews::attr(href)').extract_first()
        #print('https://www.glassdoor.com'+interview_url)

    def parse_company_interview(self, response):
        company_name = response.css('div.condensed.showHH').css('span::text').extract_first()
        if(company_name[(len(company_name)-11):] ==' Interviews' ):
            company_name = company_name[:(len(company_name)-11)]
        for review in response.css('li.empReview.cf'):
            datetime = review.css('time.date::attr(datetime)').extract_first()
            title = review.css('span.reviewer::text').extract_first()
            link = review.css('a::attr(href)').extract_first()
            location = review.css('span.authorLocation::text').extract_first()
            interview_details = review.css('p.interviewDetails.mainText::text').extract_first()
            interview_questions = review.css('span.interviewQuestion.noPadVert.truncateThis.wrapToggleStr::text').extract()
            interview_question =''
            for question in interview_questions:
                interview_question=interview_question+question+" "
            result1 = None
            result2 = None
            result3 = None
            for result in review.css('div.interviewOutcomes').css('span.middle::text').extract():
                if (result1 is None):
                    result1 = result
                else: 
                    if (result2 is None):
                        result2 = result
                    else:
                        if (result3 is None):
                            result3 = result
    
            review_id = link.split("/")[-1]
            data = {'review_id':review_id,'company_name':company_name,'datetime':datetime,'title':title,'link':('https://www.glassdoor.com'+link),'location':location,'interview_details':interview_details,'interview_question':interview_question,'result1':result1,'result2':result2,'result3':result3}
            
            fileLocation = 'crawled_data/glassdoor_interview'
            if not os.path.exists(fileLocation):
                os.makedirs(fileLocation)
            
            file = open(fileLocation+'/'+review_id+'.json', 'w')
            json.dump(data, file)
            file.close()
        url = self.pop_url()
        
        next_url = response.css('li.next').css('a::attr(href)').extract_first()
        if not (next_url is None):
            next_url = 'https://www.glassdoor.com'+next_url
            self.push_url('3 '+next_url)
        
        url = self.peek_url()
        if not (url is None):
            url_arr = url.split(" ")
            if(url_arr[0]=='1'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
            if(url_arr[0]=='2'):  
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
            if(url_arr[0]=='3'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_interview)
        else:
            os.remove("crawling.txt")
                