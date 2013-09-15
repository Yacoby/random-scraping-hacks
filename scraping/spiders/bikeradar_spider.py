import re

from scrapy.http import Request
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector

from ..items import ProductItem 
from ..morespiders import OnceCrawlSpider

class BikeRadarSpider(OnceCrawlSpider):
    name = 'BikeRadar'
    allowed_domains = ['www.bikeradar.com']
    start_urls = ['http://www.bikeradar.com']

    rules = (
        Rule(SgmlLinkExtractor(allow=('com/gear/',
                                      'com/mtb/gear/',
                                      'com/road/gear/')), callback='parse_item', follow=True),
    )

    def start_requests_impl(self):
        yield Request('http://www.bikeradar.com',
                      cookies={'_brregion': 'en-GB,confirmed',},
                      callback=self.parse)

    def extract_price(self, price_str):
        match = re.search(u'\xa3(?:([0-9]),)?([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            if match.group(1) is not None:
                return match.group(1) + match.group(2)
            return match.group(2)

    def get_itemprop(self, hxs, elm = None, cls = None, prop = None):
        if elm is None:
            elm = '*'

        if cls is not None:
            if prop is not None:
                xs = '//%s[@class="%s" and @itemprop="%s"]/text()' % (elm, cls, prop)
            else:
                xs = '//%s[@class="%s"]/text()' % (elm, cls)
        else:
            xs = '//%s[@itemprop="%s"]/text()' % (elm, prop)

        result = hxs.select(xs).extract()
        if not result:
            return None
        return ''.join(result)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        name = self.get_itemprop(hxs, elm='h2', prop='name')
        if name is None:
            return

        if name.endswith(' review'):
            name = name[:-len(' review')]

        item = ProductItem()
        item['url']  = response.url

        item['name'] = name
        item['rating'] = float(self.get_itemprop(hxs, prop='ratingValue'))/5.0
        item['reviewCount'] = 1

        item['rrp'] = self.extract_price(self.get_itemprop(hxs, elm='dd', cls='price'))
        item['manufacturers'] = [self.get_itemprop(hxs, cls='brand', prop='name')]

        yield item
