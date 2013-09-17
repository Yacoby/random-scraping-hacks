"""
A downloader middleware automatically to redirect pages containing a
rel=canonical in their contents to the canonical url (if the page itself is not the canonical one)
"""

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.url import url_is_from_spider
from scrapy.http import HtmlResponse
from scrapy import log

from scrapy.item import Item
import psycopg2
import settings
#import dal.scrapeddata

class RelCanonicalMiddleware(object):
    _extractor = SgmlLinkExtractor(restrict_xpaths=['//head/link[@rel="canonical"]'], tags=['link'], attrs=['href'])

    def process_response(self, request, response, spider):
        if isinstance(response, HtmlResponse) and response.body and getattr(spider, 'follow_canonical_links', True):
            rel_canonical = self._extractor.extract_links(response)
            if rel_canonical:
                rel_canonical = rel_canonical[0].url
                if rel_canonical != request.url and url_is_from_spider(rel_canonical, spider):
                    log.msg("Redirecting (rel=\"canonical\") to %s from %s" % (rel_canonical, request), level=log.DEBUG, spider=spider)
                    callback = lambda r: request.callback(r) if r.status == 200 else request.callback(response)
                    return request.replace(url=rel_canonical, method='GET', callback=callback)
        return response


class BikeHttpErrorMiddleware(object):
    """
    Spider Middleware
    If there is a not found error, we delete the item for that url
    """
    def __init__(self):
        connectionString = ' '.join([str(k) + '=' + str(v)
                                     for (k, v) in settings.DB.items()])
        connection = psycopg2.connect(connectionString)
        self.scraper_data = dal.scrapeddata.ScrapedData(connection)

    def process_spider_input(self, response, spider):
        if response.status == 404:
            self.scraper_data.delete_item_at_url_if_exists(response.url)

class ProductItemUnusedUrlRemoverMiddleware(object):
    """
    Spider Middleware
    If we get items back from a url, but they aren't the same url as was in the
    request we delete the url in the response object
    """
    def __init__(self):
        connectionString = ' '.join([str(k) + '=' + str(v)
                                     for (k, v) in settings.DB.items()])
        connection = psycopg2.connect(connectionString)
        self.scraper_data = dal.scrapeddata.ScrapedData(connection)

    def process_spider_output(self, response, result, spider):
        result = list(result)

        items = [item for item in result if isinstance(item, Item)]
        items_with_response_url = [item for item in items if item.get('url', None) == response.url or item.get('url', None) == None]
        if items and not items_with_response_url:
            log.msg('Got data back, but no items for the request url <%s>' % response.url, level=log.DEBUG, spider=spider)
            self.scraper_data.delete_item_at_url_if_exists(response.url)

        return result


class ProductItemUrlAppenderMiddleware(object):
    """
    Spider Middleware
    If there is no url on the result, we add the url
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if isinstance(item, Item) and 'url' in item.fields and not 'url' in item:
                item['url'] = response.url
            yield item

class InvalidScrapedItemMiddleware(object):
    """
    Spider Middleware
    If there is no valid output from a url, we ensure that if the url
    matches a scraped item it is removed
    """

    def __init__(self):
        connectionString = ' '.join([str(k) + '=' + str(v)
                                     for (k, v) in settings.DB.items()])
        connection = psycopg2.connect(connectionString)
        self.scraper_data = dal.scrapeddata.ScrapedData(connection)

    def process_spider_output(self, response, result, spider):
        result = list(result)
        if not result:
            log.msg('Parsing the url <%s> did not result in any items' % response.url, level=log.DEBUG, spider=spider)
            self.scraper_data.delete_item_at_url_if_exists(response.url)
        return result
