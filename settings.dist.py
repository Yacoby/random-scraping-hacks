
DB = {
        'dbname' : '',
        'user'   : '',
}

# Scrapy settings for bike project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#


BOT_NAME = 'bike'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = 'scrape.spiders'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5'

DOWNLOAD_DELAY=25

#LOG_LEVEL='INFO'

ITEM_PIPELINES = [
    'scraping.pipelines.BadDataFilter',
    'scraping.pipelines.HtmlCleaner',
    'scraping.pipelines.DbWriter',
]

DOWNLOADER_MIDDLEWARES = {
    'scraping.middlewares.RelCanonicalMiddleware': 1,
}

SPIDER_MIDDLEWARES = {
    #'scraping.middlewares.InvalidScrapedItemMiddleware': 1,
    'scraping.middlewares.ProductItemUrlAppenderMiddleware': 2,
    #'scraping.middlewares.BikeHttpErrorMiddleware': 3,
    #'scraping.middlewares.ProductItemUnusedUrlRemoverMiddleware': 4,
}
