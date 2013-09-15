import re

from scrapy.contrib.spiders import Rule
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector

from ..items import ProductItem
from ..morespiders import OnceCrawlSpider

class MerlinSpider(OnceCrawlSpider):
    name = 'Merlin'
    allowed_domains = ['www.merlincycles.com', 'merlincycles.com']

    rules = (
        Rule(SgmlLinkExtractor(allow=('/bike-shop/', )), callback='parse_item', follow=True),
        Rule(SgmlLinkExtractor(allow=('/sale-section/', )), ),
    )

    def start_requests_impl(self):
        yield FormRequest('http://www.merlincycles.com/ajax/Regional/setRegionalData/',
                          formdata={'currency': '1', 'country': '33'},
                          callback=self.start_parse_proper)

    def start_parse_proper(self, response):
        yield Request('http://www.merlincycles.com/', callback=self.parse)

    def extract_price(self, priceStr):
        match = re.search(u'\xa3(?:([0-9]),)?([0-9]*\\.[0-9]*)', priceStr, re.U)
        if match is None:
            return None
        else:
            if match.group(1) is not None:
                return match.group(1) + match.group(2)
            return match.group(2)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['name'] = ''.join(hxs.select('//*[@id="CenterColumnInnerInner"]/h1/text()').extract())
        item['category'] = ''.join(hxs.select("(//div[@id='ctl00_bct']//li/a)[last()]/text()").extract())

        try:
            item['image_url'] = hxs.select('//div[@class="productImage"]//img/@src').extract()[0]
        except IndexError:
            pass

        for e1 in hxs.select('//*[@class="productOptionsContainer"]'):
            for e2 in e1.select('./div[@class="productOption inStock"]'):
                option_price = ''.join(e2.select('./div/div[@class="sell"]/span/text()').extract())
                option_rrp   = ''.join(e2.select('./div/span[@class="rrp"]/span/text()').extract())

                if option_rrp:
                    item['rrp'] = self.extract_price(option_rrp)
                else:
                    item['rrp'] = self.extract_price(option_price)

                item['price'] = min(item.get('price', float('inf')), option_price)

        if not 'price' in item:
            return
        return item
