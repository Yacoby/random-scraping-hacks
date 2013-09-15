import re
from itertools import product
from urlparse import urlparse

from scrapy.contrib.spiders import Rule
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector

from ..items import ProductItem 

from ..morespiders import OnceCrawlSpider

class RoseSpider(OnceCrawlSpider):
    name = 'Rose'
    allowed_domains = ['www.rosebikes.co.uk']
    start_urls = ['http://www.rosebikes.co.uk']

    rules = (
        Rule(SgmlLinkExtractor(allow=('article/', )), callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=(r'products/(\w+/)*$',)), follow=True, callback='get_extra_pages'),
        Rule(SgmlLinkExtractor(allow=(r'products/(\w+/)*\?page',)), follow=True, callback='get_extra_pages'),
    )

    def _requests_to_follow(self, response):
        response = response.replace(body=response.body.replace('\xe2\x80\x90\xe2\x80\x90', '--'))
        return super(RoseSpider, self)._requests_to_follow(response)

    def extract_price(self, price_str):
        price_str = re.compile(r'\s', re.U).sub('', price_str)
        match = re.search(ur'\xa3(?:([0-9])\.)?([0-9]*),([0-9]*)', price_str, re.U)
        if match is None:
            return None
        else:
            if match.group(1) is not None:
                return match.group(1) + match.group(2) + '.' + match.group(3)
            return match.group(2) + '.' + match.group(3)

    def get_extra_pages(self, response):
        ''' Stupid JS links that don't have a fallback '''
        response = response.replace(body=response.body.replace('\xe2\x80\x90\xe2\x80\x90', '--'))
        hxs = HtmlXPathSelector(response)

        urlParts = urlparse(response.url)

        pages = hxs.select('//*[@id="pagination_bottom"]/span/a/text()').extract()

        for page_num in pages:
            page_url = 'http://www.rosebikes.co.uk' + urlParts.path + '?page=' + page_num
            yield Request(page_url)

    def parse_item(self, response):
        response = response.replace(body=response.body.replace('\xe2\x80\x90\xe2\x80\x90', '--'))
        hxs = HtmlXPathSelector(response)

        item = ProductItem()
        item['name'] = ''.join(hxs.select('//*[@id="product_title"]/text()').extract())

        man =  ''.join(hxs.select('//*[@id="product_detail_brand_logo"]/img/@alt').extract())
        if man != '':
            item['manufacturers'] = [man]

        try:
            item['image_url'] = hxs.select('//img[@class="productimagebox_item"]/@src').extract()[0]
        except IndexError:
            try:
                item['image_url'] = hxs.select('//a[contains(@class,"productimagebox_item")]/@href').extract()[0]
            except IndexError:
                pass

        item['category'] = ''.join(hxs.select("(//div[@id='breadcrumbs']/a)[last() - 3]/text()").extract())

        ratingCount = hxs.select('//*[@id="product_title_rating"]/div[6]/text()').extract()[0].strip('()')
        item['reviewCount'] = ratingCount

        options = []
        option_elems = hxs.select('//*[@id="product_availability_table"]/tbody/tr')
        for e in option_elems:
            color = ''.join(e.select('.//div[@class="product_color_name"]/text()').extract()).strip()
            sizes = e.select('.//div[@class="size_box" or @class="size_box selected"]/div[@class="size"]/text()').extract()

            price = self.extract_price(''.join(e.select('.//td[@class="last"]/text()').extract()).strip())
            for (option_colour, option_size) in product([color], sizes):
                name = option_colour if option_size == 'Standard' else option_colour + ' - ' + option_size
                options.append({'price': price,
                                'rrp'  : None,
                                'name' : name,})
        item['options'] = options

        return [item]
