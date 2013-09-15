import re
import urlparse

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem 
from ..morespiders import OnceCrawlSpider

class StifSpider(OnceCrawlSpider):
    name = 'StifPerformanceCycles'
    allowed_domains = ['www.stif.co.uk']
    start_urls = ['http://www.stif.co.uk']

    rules = (
        Rule(SgmlLinkExtractor(deny=('stif\.co\.uk/help/',
                                     'stif\.co\.uk/shop/',
                                    )), callback='parse_item', follow=True),
    )

    def extract_price(self, price_str):
        match = re.search(u'\xa3(?:([0-9]),)?([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            if match.group(1) is not None:
                return match.group(1) + match.group(2)
            return match.group(2)

    def make_canonical_url(self, name, url):
        match = re.search(ur'\d+$', url, re.U)
        if match is None:
            return None
        name = name.lower().replace(' ', '-')
        return 'http://www.stif.co.uk/mtb/product/%s/%s' % (name, match.group(0))

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        option_rrp = []
        options = []
        option_elems = hxs.select("//tr[@class='stk_instock']")
        for e in option_elems:
            raw_name = self.extract_all_text(e.select(".//td[@class='colone']"))
            name = raw_name[:raw_name.find(' (')]

            price = self.extract_price(self.extract_all_text(e.select(".//*[@class='newprice']")))
            rrp = self.extract_price(self.extract_all_text(e.select(".//*[@class='oldPrices']")))
            if not rrp:
                option_rrp.append(price)
            else:
                option_rrp.append(rrp)

            options.append({'name':name, 'currency': 'GBP', 'price':price,})

        if not options:
            return

        item = ProductItem()
        item['name'] = self.extract_all_text(hxs.select('//*[@id="productTabulation"]/h1/span'))
        item['url']  = self.make_canonical_url(item['name'], response.url)

        item['category'] = self.extract_all_text(hxs.select('(//*[@id="productTabulation"]/h1/a)[last()]'))

        try:
            img_src = hxs.select("//*[@class='panel a']//img/@src").extract()[0]
            item['image_url'] = urlparse.urljoin(response.url, img_src.strip())
        except IndexError:
            self.log('Failed to get image (IndexError)', level=log.WARNING)

        item['description'] = self.extract_all_text(hxs.select('//*[@id="description"]'))


        item['rrp'] = min(option_rrp)
        item['options'] = options

        return [item]
