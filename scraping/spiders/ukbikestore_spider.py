import re
import urlparse

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem
from ..morespiders import OnceCrawlSpider

class UkBikeStoreSpider(OnceCrawlSpider):
    name = 'UkBikeStore'
    allowed_domains = ['www.ukbikestore.co.uk']
    start_urls = ['http://www.ukbikestore.co.uk']

    rules = (
        Rule(SgmlLinkExtractor(), callback='parse_item', follow=True),
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

        option_rrp = []
        options = []
        option_elems = hxs.select("//form[@class='PDOR_Form']")

        if not option_elems:
            return

        for e in option_elems:
            raw_name = self.extract_all_text(e.select(".//span[@class='ProductDetailsTitle']"))
            name = raw_name[raw_name.find(',')+1:]

            rrp = self.extract_price(self.extract_all_text(e.select(".//*[@class='rrp']")))
            price = self.extract_price(self.extract_all_text(e.select(".//*[@class='Price']")))
            if rrp is None:
                option_rrp.append(price)
            else:
                option_rrp.append(rrp)

            options.append({'name':name, 'currency': 'GBP', 'price':price,})

        item = ProductItem()
        item['options'] = options
        item['rrp'] = min(option_rrp)

        item['name'] = ''.join(hxs.select("//h1[@id='_ctl0_ShopLocator']/text()").extract())

        item['category'] = ''.join(hxs.select("(//a[@class='BreadCrumb'])[2]/text()").extract()).capitalize()

        item['description'] = [''.join(hxs.select("//*[@id='ProductFullDescription']/text()").extract())]
        try:
            img_src = hxs.select("//img[@id='MainImage']/@src").extract()[0]
            item['image_url'] = urlparse.urljoin(response.url, '/' + img_src.strip())
        except IndexError:
            self.log('Failed to get image (IndexError)', level=log.WARNING)

        return [item]
