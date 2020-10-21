# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FollowersItem(scrapy.Item):
    username = scrapy.Field()
    user_id = scrapy.Field()
    node = scrapy.Field()
    target_full_name = scrapy.Field()
    target_id = scrapy.Field()
    target_username = scrapy.Field()
    target_profile_pic_url = scrapy.Field()


class FollowingItem(scrapy.Item):
    username = scrapy.Field()
    user_id = scrapy.Field()
    node = scrapy.Field()
    target_full_name = scrapy.Field()
    target_id = scrapy.Field()
    target_username = scrapy.Field()
    target_profile_pic_url = scrapy.Field()