import scrapy
from scrapy.selector import Selector
from pathlib import Path
from scrapy.crawler import CrawlerProcess
import time
import json
import os

class GlassdoorSpider(scrapy.Spider):
    name = "glassdoor_company_review"
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
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_review)
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
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_review)
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
            if(company_name[(len(company_name)-8):] ==' Reviews' ):
                company_name = company_name[:(len(company_name)-8)]    
            data = {'company_name':company_name,'logo':logo,'video':video,'website':website,'headquarter':headquarter,'size':size,
            'founded':founded,'type':type,'industry':industry,'revenue':revenue,'competitors':competitors}
                
            file = open('crawled_data/Company/'+company_name+'.json', 'w')
            json.dump(data, file)
            file.close()
            
            review_url = response.css('a.reviews::attr(href)').extract_first()
            review_url = 'https://www.glassdoor.com'+review_url
            url = self.pop_url()
            self.push_url('3 '+review_url)
            url = self.peek_url()
            if not (url is None):
                url_arr = url.split(" ")
                if(url_arr[0]=='1'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
                if(url_arr[0]=='2'):  
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
                if(url_arr[0]=='3'):
                    yield scrapy.Request(url=url_arr[1], callback=self.parse_company_review)
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
        
        data = {'company_name':company_name,'logo':logo,'video':video,'website':website,'headquarter':headquarter,'size':size,
        'founded':founded,'type':type,'industry':industry,'revenue':revenue,'competitors':competitors}
        
        fileLocation = 'crawled_data/glassdoor_company'
        if not os.path.exists(fileLocation):
            os.makedirs(fileLocation)    
        file = open(fileLocation+'/'+company_name+'.json', 'w')
        json.dump(data, file)
        file.close()
        
        review_url = response.css('a.reviews::attr(href)').extract_first()
        review_url = 'https://www.glassdoor.com'+review_url
        url = self.pop_url()
        self.push_url('3 '+review_url)
        url = self.peek_url()
        if not (url is None):
            url_arr = url.split(" ")
            if(url_arr[0]=='1'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_companies_list)
            if(url_arr[0]=='2'):  
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_detail) 
            if(url_arr[0]=='3'):
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_review)
        else:
            os.remove("crawling.txt")
        #interview_url = response.css('a.interviews::attr(href)').extract_first()
        #print('https://www.glassdoor.com'+interview_url)

    def parse_company_review(self, response):
        company_name = response.css('div.condensed.showHH').css('span::text').extract_first()
        for review in response.css('div.hreview'):
            datetime = review.css('time.date::attr(datetime)').extract_first()
            title = review.css('span.summary::text').extract_first()
            link = review.css('a.reviewLink::attr(href)').extract_first()
            rating = review.css('span.rating').css('span.value-title::attr(title)').extract_first()
            position = review.css('span.authorJobTitle::text').extract_first()
            pros = review.css('p.pros::text').extract_first()
            cons = review.css('p.cons::text').extract_first()
            adviceMgmt = review.css('p.adviceMgmt::text').extract_first()
            review_description = review.css('p.tightBot.mainText::text').extract_first()
            opinion1 = None
            opinion2 = None
            opinion3 = None
            for review_recommend in review.css('div.flex-grid.recommends').css('div.tightLt.col.span-1-3'):
                opinion_2=review_recommend.css('span.middle::text').extract_first()
                opinion_1=review_recommend.css('span.showDesk::text').extract_first()
                if not (opinion_1 is None) and not (opinion_2 is None):
                    opinion = opinion_1+' '+opinion_2
                else:
                    opinion = opinion_2
                if (opinion1 is None):
                    opinion1 = opinion
                else: 
                    if (opinion2 is None):
                        opinion2 = opinion
                    else:
                        if (opinion3 is None):
                            opinion3 = opinion
    
            
            review_id = link.split("/")[-1]
            data = {'review_id':link,'company_name':company_name,'datetime':datetime,'title':title,'link':('https://www.glassdoor.com'+link),'rating':rating,'position':position,'pros':pros,'cons':cons,'adviceMgmt':adviceMgmt,'review_description':review_description,'opinion1':opinion1,'opinion2':opinion2,'opinion3':opinion3}
            
            fileLocation = 'crawled_data/glassdoor_review'
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
                yield scrapy.Request(url=url_arr[1], callback=self.parse_company_review)
        else:
            os.remove("crawling.txt")
                