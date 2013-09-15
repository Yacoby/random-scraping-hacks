from scrapy.item import Item, Field

class ProductItem(Item):
    name          = Field()
    url           = Field()
    price         = Field()

    # ----------------------------------
    # Things below here are not required
    category      = Field()
    description   = Field()
    image_url     = Field()

    options       = Field()

    review_count  = Field()
    rating        = Field() #should be between 0 and 1 or None
    rrp           = Field()

    #This is an array of any manufacturers found on the page
    manufacturers = Field()
