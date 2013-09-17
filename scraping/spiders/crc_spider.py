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
        yield FormRequest('http://www.chainreactioncycles.com/?_DARGS=/common/frag/localePicker.jsp',
                          formdata={'_D:/atg/userprofiling/ProfileFormHandler.value.country': '',
                                    '/atg/userprofiling/ProfileFormHandler.value.country':'GB',
                                    '_D:/atg/userprofiling/ProfileFormHandler.value.currency':'' ,
                                    '/atg/userprofiling/ProfileFormHandler.value.currency':'GBP',
                                    '_D:/atg/userprofiling/ProfileFormHandler.value.language':'' ,
                                    '/atg/userprofiling/ProfileFormHandler.value.language':'en',
                                    '/atg/userprofiling/ProfileFormHandler.successURL':'http://www.chainreactioncycles.com/',
                                    '_D:/atg/userprofiling/ProfileFormHandler.successURL': '',
                                    '/atg/userprofiling/ProfileFormHandler.failureURL':'/',
                                    '_D:/atg/userprofiling/ProfileFormHandler.failureURL': '',
                                    '/atg/userprofiling/ProfileFormHandler.updateLocaleInfo':'update',
                                    '_D:/atg/userprofiling/ProfileFormHandler.updateLocaleInfo': '',
                                    '_DARGS':'/common/frag/localePicker.jsp', },
                          callback=self.parse)

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
