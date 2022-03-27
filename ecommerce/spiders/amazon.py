# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode, urljoin
import re
import json
import random

class CategorySpider(scrapy.Spider):
    name = 'amazon'
    
    user_agent = [
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.60',
              'Mozilla/5.0 (Linux; Android 4.4.3; KFTHWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/47.1.79 like Chrome/47.0.2526.80 Safari/537.36',
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
              'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
              'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
              'Roku4640X/DVP-7.70 (297.70E04154A)',
              'Mozilla/5.0 (Linux; U; Android 4.2.2; he-il; NEO-X5-116A Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30',
              'Mozilla/5.0 (Linux; Android 5.1; AFTS Build/LMY47O) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/41.99900.2250.0242 Safari/537.36',
              'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus Player Build/MMB29T)',
             'AppleTV6,2/11.1',
             'AppleTV5,3/9.1.1'      
           ]
   
   
    def start_requests(self):
       
            url = 'https://www.amazon.ca/s?bbn=4624450011&rh=n%3A4624450011%2Cp_89%3ABritax&dc&qid=1641915460&rnid=7590290011&ref=lp_4624450011_nr_p_89_2'
            yield scrapy.Request(url=url, callback=self.parse,headers={
            'User-Agent':random.choice(self.user_agent)})

 
    def parse(self,response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.ca/dp/{asin}"
            yield scrapy.Request(url=product_url, callback= self.parse_product_page, meta={'asin': asin}, headers={
            'User-Agent':random.choice(self.user_agent)})

        next_page = response.xpath("//li[@class='a-last']/a")
        
        
        if(next_page):
            next_page = response.xpath("//li[@class='a-last']/a/@href").get()
            next_page = f'https://www.amazon.ca{next_page}'
            yield scrapy.Request(url=next_page, callback= self.parse, headers={
            'User-Agent':random.choice(self.user_agent)})


    def parse_product_page(self, response):
       
        asin = response.meta['asin']
        title = response.xpath('//*[@id="productTitle"]/text()').extract_first()
        #image = re.search('"large":"(.*?)"',response.text).groups()[0]
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        bullet_points = response.xpath('//*[@id="feature-bullets"]//li/span/text()').extract()
        price = response.xpath("(//span[contains(@class,'a-price')]/span/text())[1]").get()
        colors = response.xpath("//ul[@class='a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches']/li")
        button = response.xpath("//ul[@role='radiogroup']")      
         
        if button:
            for color in colors :
                asin_color = color.xpath(".//@data-defaultasin").get()
                color_url = f"https://www.amazon.ca/dp/{asin_color}"
                yield scrapy.Request(url=color_url, callback=self.parse_color, headers={
            'User-Agent':random.choice(self.user_agent)})
        else:
            yield {
                'asin': asin,
                'Title': response.xpath('normalize-space(//span[@id="productTitle"]/text())').extract_first(),
                'Rating': rating,
                'NumberOfReviews': number_of_reviews,
                'Price': price,
                'Color':'No Color'
            }

    def parse_color(self,response):
        
        color = response.xpath("normalize-space(//span[@class='selection']/text())").get()
        title = response.xpath('normalize-space(//*[@id="productTitle"]/text())').extract_first()
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
        bullet_points = response.xpath('//*[@id="feature-bullets"]//li/span/text()').extract()
        price = response.xpath("(//span[contains(@class,'a-price')]/span/text())[1]").get()

        yield {
                'Title': title,
                'Rating': rating,
                'NumberOfReviews': number_of_reviews,
                'Price': price,
                'Color':color
            }

