import settings
import dal.items
import datetime
import psycopg2

OLD_SITE_ID = 2
NEW_SITE_ID = 3

connectionString = ' '.join([str(k) + '=' + str(v) for (k, v) in settings.DB.items()])
newDb = psycopg2.connect(connectionString)

dal = dal.items.Items(newDb)

dbSettings = settings.DB
dbSettings['dbname'] = 'bikestore'
connectionString = ' '.join([str(k) + '=' + str(v) for (k, v) in dbSettings.items()])
oldDb = psycopg2.connect(connectionString)

cursorItem = oldDb.cursor()
cursorItem.execute('SELECT id,name,url,description, review_count, rating, rrp, image_url FROM "ScrapedItem" WHERE site_id=' + str(OLD_SITE_ID))
for record in cursorItem:
    (itemId, name,url, description, review_count, rating, rrp, image_url,) = record
    print(name)

    item = {
            'name':name,
            'url':url,
            'description':description,
            'review_count':review_count,
            'rating':rating,
            'rrp':rrp,
            'image_url':image_url,
            }

    newItemId = dal.insert_or_update_item(NEW_SITE_ID, item)
    prices = {}

    cursorPrice = oldDb.cursor()
    cursorPrice.execute(('SELECT price, time FROM "ScrapedOptionPrice" sop '
                         'INNER JOIN "ScrapedOption" op ON sop.scraped_option_id = op.id '
                         'WHERE op.scraped_item_id=%s'), (itemId,))

    for priceRecord in cursorPrice:
        (price, time, ) = priceRecord
        prices[time.date()] = price

    for date,price in prices.items():
        dal.insert_price_for_item(newItemId, price, datetime.datetime.combine(date, datetime.time()))

    print('Inserted %i prices' % len(prices))

