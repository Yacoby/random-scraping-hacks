import re
import urlparse

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem
from ..morespiders import OnceCrawlSpider

class OnOneSpider(OnceCrawlSpider):
    name = 'On-One'
    allowed_domains = ['www.on-one.co.uk']
    start_urls = ['http://www.on-one.co.uk/']

    rules = (
        Rule(SgmlLinkExtractor(allow=(r'co.uk/c/q/',), deny=(r'\?sort=',)), follow=True),
        Rule(SgmlLinkExtractor(allow=(r'co.uk/i/q/',)), callback='parse_item', follow=True),
    )

    def extract_price(self, price_str):
        match = re.search(u'\xa3(?:([0-9]),)?([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            if match.group(1) is not None:
                return match.group(1) + match.group(2)
            return match.group(2)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        options = []
        option_elems = hxs.select("//div[@id='productBuyingOptions']//tr")
        for e in option_elems:
            name = self.extract_all_text(e.select('td[@class="option"]/span'))
            if not name:
                continue

            stock_status = self.extract_all_text(e.select('td[3]'))
            if 'in stock' not in stock_status.lower():
                self.log('<%s> was not in stock' % name)
                continue

            price = self.extract_price(self.extract_all_text(e.select('td[4]')))
            options.append({'name':name, 'currency': 'GBP', 'price':price,})

        if not options:
            self.log('No options founds')
            return

        item = ProductItem()
        item['name'] = self.extract_all_text(hxs.select('//*[@class="productTitle clearfix"]/h1'))

        item['category'] = self.extract_all_text(hxs.select('(//*[@class="breadcrumb"]//li/a)[last()]'))

        try:
            img_src = hxs.select("//img[@id='productMain']/@src").extract()[0]
            item['image_url'] = urlparse.urljoin(response.url, img_src.strip())
        except IndexError:
            self.log('Failed to get image (IndexError)', level=log.WARNING)

        item['description'] = self.extract_all_text(hxs.select('//*[@id="contentProduct"]/div[2]/p'))

        rrps = [self.extract_price(x) for x in hxs.select('//span[@class="rrp"]/text()').extract()]
        item['rrp'] = min(rrps) if rrps else min([option['price'] for option in options])

        item['options'] = options

        return [item]
