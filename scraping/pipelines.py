"""
This is part of the pipeline that items (when they are scraped) go down

This ensures that the scraped data is clean and put on the db
"""

import psycopg2
import HTMLParser

from scrapy import log

import settings

import dal.items

class MergeIfLooksLikeDuplicate(object):
    """
    This will alter the url (primary key) of an item if it looks very like another item
    this helps avoid duplicates in the database

    In other words, this tries to ensure that the primary key is (name, url) rather
    than url

    TODO really? Is this good? Why not do it at the DB level??
    """

    def process_item(self, item, spider):
        """ TODO implement """
        return item

class BadDataFilter(object):
    def process_item(self, item, spider):
        if not item['name']:
            log.msg('Dropped an item from <%s> as it had no name' % item['url'])
            return
        return item


class HtmlCleaner(object):
    """
    This cleans up any html left over in the text scraped from the
    sites
    """
    def __init__(self):
        self.parser = HTMLParser.HTMLParser()

    def process_item(self, item, spider):
        for key in ('name', 'category', 'description',):
            if key in item:
                item[key] = self._unescape(item[key])

        for key in ('name', 'category',):
            if key in item:
                item[key] = item[key].strip('\n\t ')

        if 'manufacturers' in item:
            manufacturers = item['manufacturers']
            for i, man in enumerate(manufacturers):
                manufacturers[i] = self._unescape(man)

        return item

    def _unescape(self, string):
        return self.parser.unescape(string)

class DbWriter(object):
    """
    Writes item data to the database. The connection remains open for as
    long as the scraper runs so that it should at all costs recover well
    from errors
    """

    def __init__(self):
        pass

    def process_item(self, item, spider):
        connectionString = ' '.join([str(k) + '=' + str(v)
                                     for (k, v) in settings.DB.items()])
        connection = psycopg2.connect(connectionString)

        items = dal.items.Items(connection)

        siteId = items.site_id(spider.name)

        items.insert_or_update_item(siteId, item)

        return item

