# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from pymongo import MongoClient

from instascraper.items import FollowersItem, FollowingItem


class InstascraperPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.insta_db

    def process_item(self, item, spider):
        if isinstance(item, FollowersItem):
            return self.handleFollowers(item, spider)
        elif isinstance(item, FollowingItem):
            return self.handleFollowing(item, spider)
        else:
            return item

    def handleFollowers(self, item, spider):
        item['target_id'] = item['node']['id']
        item['target_full_name'] = item['node']['full_name']
        item['target_username'] = item['node']['username']
        item['target_profile_pic_url'] = item['node']['profile_pic_url']

        # это можно перенести в отдельный pipeline для сохранения в DB
        doc = {
            '_id': item['user_id'],
            'username': item['username']
        }

        followers = {
            item['target_id']: {
                'full_name': item['target_full_name'],
                'username': item['target_username'],
                'profile_pic_url': item['target_profile_pic_url'],
                'node': item['node']
            }
        }
        del followers[item['target_id']]['node']['reel']

        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)
        collection.update_one({'_id': doc['_id']}, {'$addToSet': {'followers': followers}})

        return item

    def handleFollowing(self, item, spider):
        item['target_id'] = item['node']['id']
        item['target_full_name'] = item['node']['full_name']
        item['target_username'] = item['node']['username']
        item['target_profile_pic_url'] = item['node']['profile_pic_url']

        # это можно перенести в отдельный pipeline для сохранения в DB
        doc = {
            '_id': item['user_id'],
            'username': item['username']
        }

        following = {
            item['target_id']: {
                'full_name': item['target_full_name'],
                'username': item['target_username'],
                'profile_pic_url': item['target_profile_pic_url'],
                'node': item['node']
            }
        }
        del following[item['target_id']]['node']['reel']

        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)
        collection.update_one({'_id': doc['_id']}, {'$addToSet': {'following': following}})

        return item
