import re

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.regex import RegexLinkExtractor

from scrapy.selector import HtmlXPathSelector

from ..items import ProductItem
from ..morespiders import OnceCrawlSpider

class PbkSpider(OnceCrawlSpider):
    name = 'ProBikeKit'
    allowed_domains = ['www.probikekit.com']

    rules = (
        Rule(RegexLinkExtractor(allow=(r'com/uk', ),
                                deny=(r'com/review/',
                                      r'com/\w{2}/review/',
                                      r'com/\w{2}/customer/',
                                      r'com/\w{2}/enquiryform/',
                                      r'com/\w{2}/catalog/product_compare',
                                      r'\?(?!p=)', #match everything starting with a ? except ?p=
                                      r'\?p=.*&',
                                      r'com/\w{2}/geolocator/',
                                      r'com/\w{2}/sendfriend/',
                                      r'__SID', #this is an ugly hack due to the failing of the regex link extractor
                                      )),
             callback='parse_item', follow=True),
    )

    #this forces price etc
    start_urls = ['http://www.probikekit.com/us/geolocator/index/index/code/gbp/']


    def extract_price(self, price_str):
        match = re.search(u'\xa3([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            return match.group(1)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        if hxs.select('//div[@class="sorter"]').extract():
            return

        item = ProductItem()
        item['name'] = self.extract_all_text(hxs.select('//div[@class="product-name"]'))
        if not item['name']:
            return

        item['rrp'] = self.extract_price(self.extract_all_text(hxs.select('//*[@class="old-price"]')))
        item['category'] = ''.join(hxs.select("(//div[@class='breadcrumbs']//a)[last()]/text()").extract())

        item['manufacturers'] = [brand for brand in hxs.select('//div[@class="brands"]/a/img/@alt').extract()]
        item['image_url'] = hxs.select('//a[@id="main-image"]/img/@src').extract()[0]

        item['options'] = []
        option_elem = hxs.select('//table[@id="super-product-table"]//tr[@class="even" or @class="odd"]')
        for elem in option_elem:
            if elem.select('.//p[@class="group-product-out-of-stock"]').extract():
                continue

            name = self.extract_all_text(elem.select('.//*[@class="group_options_option"]'))
            price = self.extract_price(self.extract_all_text(elem.select('.//*[@class="price"]')))

            item['options'].append({'name':name, 'price':price,})

        return item
