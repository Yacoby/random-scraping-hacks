import datetime

class Items:
    def __init__(self, connection):
        self.connection = connection

    def site_id(self, name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id FROM "sites" WHERE name=%s', (name,))
        if not cursor.rowcount:
            return None
        return cursor.fetchone()[0]

    def insert_or_update_item(self, siteId, item):
        cursor = self.connection.cursor()

        cursor.execute('SELECT id FROM "items" WHERE url=%s', (item['url'],))
        result = cursor.fetchone()

        if result is None:
            cursor.execute(('INSERT INTO "items" '
                            '(name, url, description, review_count, rating, rrp, image_url, site_id) '
                            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id'),
                            (item['name'],
                             item['url'],
                             item.get('description', None),
                             item.get('reviewCount', None),
                             item.get('rating', None),
                             item.get('rrp', None),
                             item.get('image_url', None),
                             siteId,))
            (itemId,) = cursor.fetchone()

        else:
            cursor.execute(('UPDATE "items" SET name=%s, '
                            'description=%s, review_count=%s, rating=%s, rrp=%s, image_url=%s '
                            'WHERE url=%s '),
                (item['name'],
                 item.get('description', None),
                 item.get('reviewCount', None),
                 item.get('rating', None),
                 item.get('rrp', None),
                 item.get('image_url', None),
                 item['url']))
            (itemId,) = result

        self.connection.commit()
        return itemId

    def insert_price_for_item(self, itemId, price, datetime=datetime.datetime.now()):
        cursor = self.connection.cursor()
        cursor.execute(('INSERT INTO "prices" '
                        '(item_id,date,price) '
                        'VALUES (%s, %s, %s) RETURNING id'),
                        (itemId,
                         datetime,
                         price,))
        (priceId,) = cursor.fetchone()
        return priceId
