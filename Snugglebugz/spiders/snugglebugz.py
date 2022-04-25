# -*- coding: utf-8 -*-
#from _typeshed import Self
from unittest import skipUnless
from urllib import parse
import scrapy
from scrapy.http.request import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlencode, urljoin, urlparse,parse_qs
import json
import urllib
from snugglebugz.utils import API,BRAND,category
from scrapy.crawler import CrawlerProcess

URL = 'https://www.snugglebugz.ca/categories/infant-car-seats?page=1'

#def get_url(url):
#    payload = {'api_key': API, 'url': url}
#    #proxy_url = f'http://api.scraperapi.com/?api_key={API}&url={URL}' 
#    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
#    return proxy_url

class ArticlesSpider(scrapy.Spider):
    name = 'snugglebugz'
    allowed_domains = ['www.snugglebugz.ca']
    
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.60'
   
   
  
    def start_requests(self):
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self,response):
        urls = response.xpath("//a[@class='product-summary__name-link']")
        for url in urls:
            item_url= url.xpath(".//@href").get()
            item_url = f'https://www.snugglebugz.ca{item_url}'
            yield scrapy.Request(url=item_url, callback= self.parse_item)
            last_page = url.xpath("//div[@class='view']/p/text()").get()

        if last_page != 'No products found.':
            url_parsed = urlparse(response.request.url)
            query_string = parse_qs(url_parsed.query)
            page = json.loads(query_string.get('page')[0])
            page += 1
            page_url = f'https://{url_parsed.netloc}{url_parsed.path}?page={page}'
            print('PAGE URL: ',page_url)
            yield scrapy.Request(url=page_url, callback=self.parse)

        
    def parse_item(self, response):
            brand = response.xpath("(//span[@class='product-details__brand-name']/a/text())[1]").get()
            color_button = response.xpath("//input[@name='colour']")
            color_frame = response.xpath("//input[@name='frame']")
            frame = response.xpath("//select[@name='frame']") 
            color = response.xpath("//select[@name='colour']")  
  
            
            #by color button
            if color_button :
               color_urls = response.xpath("//a[contains(@class,'option-button--colour')]") 
               for colorUrl in color_urls :
                   color_url= colorUrl.xpath(".//@href").get()
                   color_url=f'https://www.snugglebugz.ca{color_url}'
                   yield scrapy.Request(url= color_url,callback= self.parse_item_color)
            #by frame button
            elif color_frame :
                frame_urls = response.xpath("//a[contains(@class,'option-button--frame')]") 
                for frameURL in frame_urls :
                   frame_url= frameURL.xpath(".//@href").get()
                   frame_url=f'https://www.snugglebugz.ca{frame_url}'
                   yield scrapy.Request(url= frame_url,callback= self.parse_item_color)
            #by frame selection
            elif  frame:
                frames = response.xpath("//select[@name='frame']/option")
                for frame in frames :
                    frame_color = frame.xpath(".//@value").get()
                    frame_value = {'frame' : frame.xpath(".//@value").get()}
                    frame_encoded = urllib.parse.urlencode(frame_value)
                    frame_url= f'{response.request.url}&{frame_encoded}'
                    print('FRAME URL : ', frame_url)
                    print('FRAME COLOR : ', frame_color)
                    if frame_color:
                        yield scrapy.Request(url= frame_url,
                                             callback= self.parse_item_frame,
                                             meta={'frame':frame_color})
            #by color selection
            elif  color:
                colors = response.xpath("//select[@name='colour']/option")
                for color in colors :
                    color_item = color.xpath(".//@value").get()
                    color_value = {'colour' : color.xpath(".//@value").get()}
                    color_encoded = urllib.parse.urlencode(color_value)
                    color_url= f'{response.request.url}&{color_encoded}'
                    print('COLOR URL : ', color_url)
                    print('COLOR ITEM : ', color_item)
                    if color_item:
                        yield scrapy.Request(url= color_url,
                                             callback= self.parse_item_frame,
                                             meta={'frame':color_item})
            else :
                price = response.xpath("normalize-space(//p[@class='product-prices__price']/span/text())").get()
                sku= response.xpath("(//div[@class='product-details__id-sku']/span/text())[2]").get()
                name = response.xpath("//h1[@class='product-details__name']/text()").get()
                if price :
                    yield {
                            'category': category(URL),
                            'brand': brand,
                            'sku': sku,
                            'name': name,
                            'color': 'None',
                            'price':price,
                            'price_discounted':'No',
                            'price_original': price
                     }
                else:
                    yield {
                            'category': category(URL),
                            'brand': brand,
                            'sku': sku,
                            'name': name,
                            'color': 'No',
                            'price': price,
                            'price_discounted': response.xpath("normalize-space((//strong[@class='product-prices__price--sale']/text())[1])").get(),
                            'price_original': response.xpath("(//s[@class='product-prices__price--original']/text())[1]").get()
                        }
   

    def parse_item_color(self, response):
        
        brand = response.xpath("(//span[@class='product-details__brand-name']/a/text())[1]").get()
        color = response.xpath("//span[@class='property__text']/text()").get()
        color = color.replace('Colour: ','')
        color = color.replace('Frame: ','')
        price = response.xpath("normalize-space(//p[@class='product-prices__price']/span/text())").get()
        sku= response.xpath("(//div[@class='product-details__id-sku']/span/text())[2]").get()
        name = response.xpath("//h1[@class='product-details__name']/text()").get()
        price_discounted = response.xpath("normalize-space((//strong[@class='product-prices__price--sale']/text())[1])").get()    
        price_original =response.xpath("(//s[@class='product-prices__price--original']/text())[1]").get()
       
        print('FRAME COLOR : ', color)
        if price :
            yield {
                'category': category(URL),
                'brand': brand,
                'sku': sku,
                'name': name,
                'color': color,
                'price': price,
                'price_discounted':'No',
                'price_original': price
                }
        else :
             yield {
                'category':category(URL),
                'brand': brand,
                'sku': sku,
                'name': name,
                'color': color,
                'price': 'None',
                'price_discounted': price_discounted,
                'price_original': price_original 
                }


    def parse_item_frame(self,response):
        
        brand = response.xpath("(//span[@class='product-details__brand-name']/a/text())[1]").get()
        frame = response.meta['frame']
        price = response.xpath("normalize-space(//p[@class='product-prices__price']/span/text())").get()
        sku= response.xpath("(//div[@class='product-details__id-sku']/span/text())[2]").get()
        name = response.xpath("//h1[@class='product-details__name']/text()").get()
        price_discounted = response.xpath("normalize-space((//strong[@class='product-prices__price--sale']/text())[1])").get()    
        price_original =response.xpath("(//s[@class='product-prices__price--original']/text())[1]").get()
           
        print('FRAME : ', frame)
        
        if price :
            yield {
                'category': category(URL),
                'brand': brand,
                'sku': sku,
                'name': name,
                'color': frame,
                'price': price,
                'price_discounted':'No',
                'price_original': price
                }
        else :
             yield {
                'category':category(URL),
                'brand': brand,
                'sku': sku,
                'name': name,
                'color': frame,
                'price': 'None',
                'price_discounted': price_discounted,
                'price_original': price_original
                }


#process = CrawlerProcess(settings={
#    'FEED_URI' : 'snugglebugz.csv',
#    'FEED_FORMAT': 'csv'
#})
#
#process.crawl(ArticlesSpider)
#process.start()