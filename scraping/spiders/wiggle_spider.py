import re
import urlparse

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.http import FormRequest

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem 
from ..morespiders import OnceCrawlSpider

class WiggleSpider(OnceCrawlSpider):
    name = 'Wiggle'
    allowed_domains = ['www.wiggle.co.uk']
    start_urls = ['http://www.wiggle.co.uk/']

    rules = (
        Rule(SgmlLinkExtractor(deny=('wiggle\.co\.uk/mywishlist/',
                                     'wiggle\.co\.uk/secure/',
                                     'wiggle\.co\.uk/h/option/',
                                     'wiggle\.co\.uk/returns/',
                                     'wiggle\.co\.uk/basket/add/',
                                     'wiggle\.co\.uk/basket\?',
                                     'wiggle\.co\.uk/basket$',
                                     'wiggle\.co\.uk/view/Mobile',
                                     'wiggle\.co\.uk/mywishlist',
                                     r'curr=\w+',
                                     r'(\?(?!g=\d+).*)$',
                                     r'\?g=\d+.+$',
                                     )), callback='parse_item', follow=True),
    )

    def start_requests_impl(self):
        yield FormRequest('http://www.wiggle.co.uk/internationaloptions/update',
                          formdata={'langId': 'en',
                                    'currencyId': 'GBP',
                                    'countryId' : '1',
                                    'action' : 'Update',
                                    'returnUrl' : '/',
                                    'cancelUrl': '/'},
                          callback=self.parse)

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

        name_result = hxs.select("//*[@itemprop='name']/text()").extract()

        if not name_result:
            return

        item = ProductItem()
        item['name'] = ''.join(name_result)

        item['category'] = ''.join(hxs.select("(//div[@id='breadCrumbs']//li/a)[last()]/text()").extract())

        try:
            img_src = hxs.select("//*[@itemprop='image']/@src").extract()[0]
            image_url = urlparse.urljoin(response.url, img_src.strip())
            if image_url != 'http://www.wigglestatic.com/images/imagecomingsoon-med.jpg?w=350&h=350&a=7':
                item['image_url'] = image_url
        except IndexError:
            self.log('Failed to get image (IndexError)', level=log.WARNING)

        rc = ''.join(hxs.select("//*[@itemprop='reviewCount']/text()").extract())
        if rc != '':
            item['review_count'] =  int(rc)
            if item['review_count']:
                item['rating'] =  float(''.join(hxs.select("//*[@itemprop='ratingValue']/text()").extract()))/5

        item['manufacturers'] = [''.join(hxs.select("//*[@itemprop='manufacturer']/text()").extract())]
        item['description'] = [''.join(hxs.select("//*[@itemprop='description']/text()").extract())]

        rrp_result = hxs.select("//div[@class='listprice']/small/text()").extract()
        item['rrp'] = self.extract_price(''.join(rrp_result))

        price_result = hxs.select("//div[@class='Wprice']/text()").extract()
        price = self.extract_price(''.join(price_result))

        item['price'] = price

        options = []
        option_elems = hxs.select("//tr[@class='buythisitem']")

        for e in option_elems:
            if not e.select("td[@class='wishlist_it']/a"):
                continue
           
            s = "*[not(@class='wishlist_it') and following-sibling::*[@class='wishlist_it']]/strong/text()"
            name = ' '.join(e.select(s).extract())

            options.append({'name':name, 'currency': 'GBP', 'price':price,})

        if not options:
            return
        item['options'] = options

        return [item]
