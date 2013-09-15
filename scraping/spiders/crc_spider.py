import re
import urlparse
from functools import partial

from scrapy.contrib.spiders import Rule
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector
from scrapy import log

from ..items import ProductItem 
from ..morespiders import OnceCrawlSpider

class CrcSpider(OnceCrawlSpider):
    name = 'ChainReactionCycles'
    allowed_domains = ['www.chainreactioncycles.com']

    rules = (
        Rule(SgmlLinkExtractor(allow=(r'\.com/.*rp-prod[0-9]+$', )), callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=(r'\.com/f=[0-9+],[0-9]+', )), follow=False),
        Rule(SgmlLinkExtractor(allow=(r'\.com', )), follow=True),
    )

    #this forces price etc
    start_urls = ['http://www.chainreactioncycles.com/']

    def __init__(self, *a, **kw):
        super(CrcSpider, self).__init__(*a, **kw)
        self.has_sent_man = False

    def extract_price(self, price_str):
        match = re.search(u'\xa3([0-9]*\\.[0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            return match.group(1)

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['url'] = response.url
        item['name'] = ''.join(hxs.select("//*[@itemprop='name']/@content").extract())
        item['category'] = ''.join(hxs.select("//table[@class='Table27']//td[1]/a[last()]/text()").extract())

        #don't care that much if this fails
        try:
            img_src = hxs.select("//img[@id='ModelsDisplayStyle4_ImgModel']/@src").extract()[0]
            img_comming_soon = 'http://www.chainreactioncycles.com/Images/Models/Full/0.gif'
            if img_src != img_comming_soon:
                item['image_url'] = urlparse.urljoin(response.url, img_src.strip())
        except IndexError:
            self.log('Failed to get image (IndexError)', level=log.WARNING)
        
        #avoids filling up my log
        if self.has_sent_man is False:
            item['manufacturers'] = hxs.select("//select[@id='BrandID']/option/text()").extract()

        rrps = []
        options = []
        option_elems = hxs.select("//tr[@class='BackGround15']")
        for e in option_elems:
            stock_status_1 = ''.join(e.select('td[2]/text()').extract())
            stock_status_2 = ''.join(e.select('td[3]/text()').extract())
            if stock_status_1.lower() != 'in stock' and stock_status_2.lower() != 'in stock':
                continue

            maybe_names = e.select('td[3]//a/text()').extract() + e.select('td[4]//a/text()').extract()
            if len(maybe_names):
                name = maybe_names[0]
            else:
                name = item['name']

            price_info = ' '.join(e.select(".//table[@cellspacing='0' and @cellpadding='0']/tr/td/text()").extract())

            if "RRP" in price_info:
                price, rrp = [self.extract_price(x) for x in price_info.split("RRP")]
            else:
                rrp = price = self.extract_price(price_info)

            options.append({'name':name, 'price':price,})
            rrps.append(rrp)

        if not options:
            self.log('No options found')
            return
        item['options'] = options
        item['rrp'] = min(rrps)

        ratings_data = ''.join(hxs.select('//*[@id="ModelsDisplayStyle4_LblRating"]/text()').extract())

        self.has_sent_man = True

        if 'Avg' in ratings_data:
            #there are reviews, so make a request to parse review page
            rx = r'http://www\.chainreactioncycles\.com/Models\.aspx\?ModelID=([0-9]+)$'
            review_url = 'http://www.chainreactioncycles.com/Reviews.aspx?ModelID=' + re.match(rx, response.url).group(1)

            return Request(review_url, callback=partial(self.parse_review, item), priority=1)
        else:
            return item

    def parse_review(self, item, response):
        hxs = HtmlXPathSelector(response)
        item['reviewCount'] = hxs.select('//*[@id="LblNumberOfReviewsValue"]/text()').extract()[0]
        item['rating'] = float(hxs.select('//*[@id="LblReviewsAverageValue"]/text()').extract()[0])/5
        return item
