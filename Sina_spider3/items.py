# encoding=utf-8


from scrapy import Item, Field


class InterestingArea(Item):
    content=Field()
    review_url=Field()
    review=Field()
