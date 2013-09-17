import re
import urlparse
from functools import partial

from scrapy.contrib.spiders import Rule
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem 
from ..morespiders import OnceCrawlSpider

class CrcSpider(OnceCrawlSpider):
    name = 'ChainReactionCycles'
    allowed_domains = ['www.chainreactioncycles.com']

    rules = (
        Rule(SgmlLinkExtractor(allow=(r'rp-prod[0-9]+$', )), callback='parse_item'),
        Rule(SgmlLinkExtractor(deny=(r'f=[0-9]+,[0-9]+', )), follow=True),
    )

    def __init__(self, *a, **kw):
        super(CrcSpider, self).__init__(*a, **kw)
        self.has_sent_man = False

    def extract_price(self, price_str):
        match = re.search(u'\xa3([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            return match.group(1)

    def start_requests_impl(self):
        localization_cookies = {
                'languageCode':'en',
                'currencyCode':'GBP',
                'countryCode':'GB',
        }
        yield Request('http://www.chainreactioncycles.com/',cookies=localization_cookies)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['url'] = response.url
        item['name'] = ''.join(hxs.select("//*[@itemprop='name']/@content").extract())
        item['name'] = item['name'] or ''.join(hxs.select("//*[@class='product_title']/text()").extract())

        price_str = ''.join(hxs.select('//*[@id="crc_product_rp"]/text()').extract())
        item['price'] = self.extract_price(price_str)

        rrp_str = ''.join(hxs.select('//*[@id="crc_product_rrp"]/text()').extract())
        item['rrp'] = self.extract_price(rrp_str)

        return item
