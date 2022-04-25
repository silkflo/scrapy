BOT_NAME = 'Tjs'
DOWNLOAD_TIMEOUT = 540
SPIDER_MODULES = ['Tjs.spiders']
NEWSPIDER_MODULE = 'Tjs.spiders'
CONCURRENT_REQUESTS = 5
#RETRY_TIMES = 5
#DOWNLOAD_DELAY = 5
DOWNLOADER_MIDDLEWARES = {
    'Tjs.middlewares.CustomProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
} 
ITEM_PIPELINES = {
    'Tjs.pipelines.TjsPipeline': 300,
}
COOKIES_ENABLED = True
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.closespider.CloseSpider': 1
}
ROBOTSTXT_OBEY = False