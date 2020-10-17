import scrapy
from scrapy.http import HtmlResponse
from instascraper.items import FollowersItem, FollowingItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def __init__(self, login, encrypted_pwd, users_to_scrape):
        self.insta_login = login
        self.insta_pwd = encrypted_pwd
        self.users_to_scrape = users_to_scrape

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.parse_authentication_result,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_authentication_result(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for username in self.users_to_scrape:
                yield response.follow(
                    f'/{username}',
                    callback=self.parse_user,
                    cb_kwargs={'username': username}
                )

    def parse_user(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        variables_followers = {
            'id': user_id,
            'include_reel': True,
            'fetch_mutual': True,
            'first': 24
        }
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables_followers)}'
        yield response.follow(
            url_followers,
            callback=self.parse_followers,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables_followers': deepcopy(variables_followers)
            }
        )

        variables_following = {
            'id': user_id,
            'include_reel': True,
            'fetch_mutual': False,
            'first': 24
        }
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables_following)}'
        yield response.follow(
            url_following,
            callback=self.parse_following,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'variables_following': deepcopy(variables_following)
            }
        )

    def parse_followers(self, response: HtmlResponse, username, user_id, variables_followers, first=12, fetch_mutual=False):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info.get('has_next_page'):
            variables_followers['after'] = page_info['end_cursor']
            variables_followers['first'] = first
            variables_followers['fetch_mutual'] = fetch_mutual

            url_posts = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables_followers)}'
            yield response.follow(
                url_posts,
                callback=self.parse_followers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_followers': deepcopy(variables_followers),
                           'first': first,
                           'fetch_mutual': fetch_mutual}
            )

        edges = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for edge in edges:
            item = FollowersItem(
                username=username,
                user_id=user_id,
                node=edge['node']
            )
            yield item

    def parse_following(self, response: HtmlResponse, username, user_id, variables_following, first=12, fetch_mutual=False):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info.get('has_next_page'):
            variables_following['after'] = page_info['end_cursor']
            variables_following['first'] = first
            variables_following['fetch_mutual'] = fetch_mutual

            url_posts = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables_following)}'
            yield response.follow(
                url_posts,
                callback=self.parse_following,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_following': deepcopy(variables_following),
                           'first': first,
                           'fetch_mutual': fetch_mutual}
            )

        edges = j_data.get('data').get('user').get('edge_follow').get('edges')
        for edge in edges:
            item = FollowingItem(
                username=username,
                user_id=user_id,
                node=edge['node']
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
