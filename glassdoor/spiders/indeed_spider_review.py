import scrapy
from scrapy.selector import Selector
from pathlib import Path
from scrapy.crawler import CrawlerProcess
import time
import json
import os

class GlassdoorSpider(scrapy.Spider):
    name = "indeed_company_review"
    def start_requests(self):  
        o_url ='https://www.indeed.com/companies'
        if hasattr(self, 'keyword'):
            if not (self.keyword is None) and len(self.keyword)>0:
                keyword = self.keyword
                o_url ='https://www.indeed.com/cmp?from=discovery-cmp-front-door&zrpBack=%2Fcompanies&q='+keyword
        
        

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
        list_of_company_url = []
        for quote in response.css('div.cmp-PopularCompaniesWidget'):
            #company_name = quote.css('a.tightAll::text').extract_first()
            #href =  quote.css('a.tightAll::attr(href)').extract_first()
            href = quote.css('div.cmp-PopularCompaniesWidget-companyName').css('a::attr(href)').extract_first()
            url = 'https://www.indeed.com'+href
            list_of_company_url.append(url)
        
        for quote in response.css('div.company_result_title'):    
            href = quote.css('div.company_result_title').css('a::attr(href)').extract_first()
            url = 'https://www.indeed.com'+href
            list_of_company_url.append(url)
        
        list_of_company_url.reverse()
        href = response.css('div.cmp-company-tile-blue-name').css('a::attr(href)').extract_first()
        if not(href is None):
            url = 'https://www.indeed.com'+href
            list_of_company_url.append(url)    
        
        
        next_url = response.xpath('//span[@id=\'page_nav_next\']//a[@data-tn-element=\'next-link\']/@href').extract_first()
        
        url = self.pop_url()
        
        if not (next_url is None):
            next_url = 'https://www.indeed.com'+next_url
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

            
    def parse_company_detail(self, response):
        company_name = response.css('div.cmp-company-name::text').extract_first().strip()
        logo = response.xpath('//div[@id=\'cmp-header-logo\']/img/@src').extract_first()
        website = response.xpath('//a[@data-tn-element=\'companyLink[]\']/@href').extract()
        headquarter = response.xpath('//dl[@id=\'cmp-company-details-sidebar\']/dd[preceding-sibling::dt/text()[1]=\'Headquarters\']/text()').extract_first()
        industry = response.xpath('//dl[@id=\'cmp-company-details-sidebar\']/dd[preceding-sibling::dt/text()=\'Industry\']//a[@data-tn-element=\'industryLink\']/text()').extract_first()
        size = response.xpath('//dl[@id=\'cmp-company-details-sidebar\']/dd[preceding-sibling::dt/text()=\'Employees\']/text()').extract_first()
        revenue = response.xpath('//dl[@id=\'cmp-company-details-sidebar\']/dd[preceding-sibling::dt/text()=\'Revenue\']/text()').extract_first()
       
        data = {'company_name':company_name,'logo':logo,'website':website,'headquarter':headquarter,'size':size,'revenue':revenue,
        'industry':industry}
        
        fileLocation = 'crawled_data/indeed_company'
        if not os.path.exists(fileLocation):
            os.makedirs(fileLocation)
        
        file = open('crawled_data/indeed_company/'+company_name+'.json', 'w')
        json.dump(data, file)
        file.close()
            
        review_url = response.xpath('//a[@data-tn-element=\'reviews-countLink\']/@href').extract_first()
        review_url = 'https://www.indeed.com'+review_url
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
        company_name = response.css('div.cmp-company-name::text').extract_first().strip()
        for review in response.css('div.cmp-review-container'):
            review_id = review.css('div.cmp-review::attr(data-tn-entityid)').extract_first()
            datetime = review.css('span.cmp-review-date-created::text').extract_first()
            title = review.css('div.cmp-review-title').css('span::text').extract_first()
            position = review.css('span.cmp-reviewer::text').extract_first()
            location = review.css('span.cmp-reviewer-job-location::text').extract_first()
            
            pros = review.css('div.cmp-review-pro-text::text').extract_first()
            cons = review.css('div.cmp-review-con-text::text').extract_first()
            review_description = review.css('span.cmp-review-text::text').extract_first()
            
            work_life_balance_rating = review.css('span.cmp-Rating-on::attr(style)').extract()[0].split(':')[1].split('.')[0].strip()
            benefit_rating = review.css('span.cmp-Rating-on::attr(style)').extract()[1].split(':')[1].split('.')[0].strip()
            job_prospect_rating = review.css('span.cmp-Rating-on::attr(style)').extract()[2].split(':')[1].split('.')[0].strip()
            management_rating = review.css('span.cmp-Rating-on::attr(style)').extract()[3].split(':')[1].split('.')[0].strip()
            job_culture_rating = review.css('span.cmp-Rating-on::attr(style)').extract()[4].split(':')[1].split('.')[0].strip()
            
            overall_rating = (int(work_life_balance_rating)+int(benefit_rating)+int(job_prospect_rating)+int(management_rating)+int(job_culture_rating))/100
            
            data = {'review_id':review_id,'company_name':company_name,'datetime':datetime,'title':title,'rating':overall_rating,'position':position,'location':location,'pros':pros,'cons':cons,'review_description':review_description,
            'work_life_balance_rating':(int(work_life_balance_rating)/20),'benefit_rating':(int(benefit_rating)/20),'job_prospect_rating':(int(job_prospect_rating)/20),'management_rating':(int(management_rating)/20),'job_culture':(int(job_culture_rating)/20)}
            
            fileLocation = 'crawled_data/indeed_review'
            if not os.path.exists(fileLocation):
                os.makedirs(fileLocation)
            file = open(fileLocation+'/'+company_name+'_'+review_id+'.json', 'w')
            json.dump(data, file)
            file.close()
        url = self.pop_url()
        
        next_url = response.xpath('//a[@data-tn-element=\'next-page\']/@href').extract_first()
       
        if not (next_url is None):
            next_url = 'https://www.indeed.com'+next_url
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
                