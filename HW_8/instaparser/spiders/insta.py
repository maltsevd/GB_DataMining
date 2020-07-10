import scrapy
from scrapy.http import HtmlResponse
from HW_8.instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from scrapy.loader import ItemLoader


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = ''
    insta_pwd = ''
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_user = ['aiwithpython', 'eidos_wed']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parse_user:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 24}
        followers_url = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        following_url = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            following_url,
            callback=self.get_followers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'type': 'following'}         #variables ч/з deepcopy во избежание гонок
        )
        yield response.follow(
            followers_url,
            callback=self.get_followers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'type': 'follower'}         #variables ч/з deepcopy во избежание гонок
        )

    def get_followers(self, response: HtmlResponse, username, user_id, variables, type):
        j_data = json.loads(response.text)
        if type == 'follower':
            page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
            followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        else:
            page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
            followers = j_data.get('data').get('user').get('edge_follow').get('edges')
        for f in followers:
            loader = ItemLoader(item=InstaparserItem(), response=response)
            loader.add_value('user_id', f['node']['id'])
            loader.add_value('user_name', f['node']['username'])
            loader.add_value('full_name', f['node']['full_name'])
            loader.add_value('user_photo', f['node']['profile_pic_url'])
            loader.add_value('source', username)
            loader.add_value('type', type)
            yield loader.load_item()
        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            if type == 'follower':
                followers_url = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            else:
                followers_url = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                followers_url,
                callback=self.get_followers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'type': type}
            )

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
