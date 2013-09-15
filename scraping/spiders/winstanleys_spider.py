import re

from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.selector import HtmlXPathSelector

from ..items import ProductItem
from ..morespiders import OnceCrawlSpider

class WinstanleysSpider(OnceCrawlSpider):
    name = 'Winstanleys'
    allowed_domains = ['www.winstanleysbikes.co.uk']
    start_urls = ['http://www.winstanleysbikes.co.uk/']

    rules = (
        Rule(SgmlLinkExtractor(allow=(r'.co.uk/category/',)), follow=True),
        Rule(SgmlLinkExtractor(allow=(r'.co.uk/product/',)), callback='parse_item', follow=True),
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

        option_data = []
        option_elems = hxs.select("//*[@id='item_Tbl']//tr")
        for e in option_elems:
            key = self.extract_all_text(e.select('td[1]')).strip().strip(':')
            value = self.extract_all_text(e.select('td[2]')).strip()

            if key.lower() == 'name':
                current_option_data = {}
                option_data.append(current_option_data)

            current_option_data[key] = value

        options = []
        product_name = None
        product_rrp_list = []
        for option in option_data:
            if not option['Availability'].startswith('In Stock'):
                continue
            product_name = option['Name']

            price_str = option['Price']
            price = self.extract_price(price_str)
            if 'RRP' in price_str:
                rrp = self.extract_price(price_str.split('RRP')[1])
            else:
                rrp = price
            product_rrp_list.append(rrp)

            option_name_keys = set(option.keys()) - set(('Name', 'Price', 'Availability', 'Qty', 'Product Code',))
            name = ', '.join([option[key] for key in option_name_keys])
            if not name:
                name = product_name

            options.append({'name':name, 'currency': 'GBP', 'price':price,})

        if not options:
            self.log('No options founds')
            return

        item = ProductItem()
        item['name'] = product_name
        item['rrp']  = min(product_rrp_list)

        img_onclick = hxs.select("//img/@onclick").extract()[0]
        img_src_match = re.search(r'open\("(.*(jpg|png))', img_onclick)
        if img_src_match:
            item['image_url'] = 'http://www.winstanleysbikes.co.uk' + img_src_match.group(1)
        else:
            self.log('Could not find image in match <%s>' % img_onclick)

        item['options'] = options

        return [item]
