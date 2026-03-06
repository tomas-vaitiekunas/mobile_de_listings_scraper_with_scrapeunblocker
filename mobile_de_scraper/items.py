import scrapy


class CarListingItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    registration_date = scrapy.Field()
    mileage = scrapy.Field()
    power = scrapy.Field()
    seller_type = scrapy.Field()
    location = scrapy.Field()
