import logging
import psycopg2

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request, HtmlResponse
from scrapy import log

import settings
#import dal.scrapeddata

class PythonLogToScrapyLogHandler(logging.Handler):
    def flush(self):
        pass

    def emit(self, record):
        log.msg(self.format(record))

class OnceCrawlSpider(CrawlSpider):
    '''
    I am not convinced that the crawl spider ensures it doesn't crawl already
    seen urls. This ensures it doesn't
    TODO check
    '''

    def __init__(self, *a, **kw):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(message)s')

        handler = PythonLogToScrapyLogHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        super(OnceCrawlSpider, self).__init__(*a, **kw)

    def start_requests(self):
        initial = [req for req in self.start_requests_impl()]
    #    last_initial = initial[len(initial)-1]
    #    c = last_initial.callback
    #    last_initial.callback = lambda *a: self.gen(c, *a)
        return initial

    #def gen(self, callback, *a):
    #    if not callback:
    #        callback = self.parse

    #    for i in callback(*a):
    #        yield i

    #    connectionString = ' '.join([str(k) + '=' + str(v)
    #                                 for (k, v) in settings.DB.items()])
    #    connection = psycopg2.connect(connectionString)
    #    scraped_data = dal.scrapeddata.ScrapedData(connection)
    #    results = scraped_data.get_all_urls_from_site(self.name)
    #    connection.close()

    #    for (url,) in results:
    #        r = Request(url=url, callback=self._response_downloaded)
    #        r.meta.update(rule=0, link_text='')
    #        yield r

    def parse_item(self, response):
        raise NotImplementedError('parse_item should be overridden in the spider class')

    def start_requests_impl(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def extract_all_text(self, element, join=''):
        return join.join(element.select('.//text()').extract()).strip()
