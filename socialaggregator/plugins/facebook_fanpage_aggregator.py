import httplib2

from facebook import GraphAPI
from datetime import datetime

from django.conf import settings
from .generic import GenericAggregator


class Aggregator(GenericAggregator):

    APP_ID = settings.EDSA_FB_APP_ID
    APP_SECRET = settings.EDSA_FB_APP_SECRET

    datetime_format = "%Y-%m-%dT%H:%M:%S+0000"

    def init_connector(self):
        req = httplib2.Http()
        uri = "https://graph.facebook.com/oauth/access_token?client_id=%s"\
              "&client_secret=%s"\
              "&grant_type=client_credentials" % (self.APP_ID, self.APP_SECRET)
        resp, content = req.request(uri, "GET")
        access_token = str(content).split('"')[3]
        self.connector = GraphAPI(access_token)

    def search(self, query):
        res = self.connector.get_object("%s/posts" % query)
        datas = []
        for post in res['data']:
            if 'message' in post:
                if 'link' in post:
                    link = post['link']
                    media_url_type = 'url'
                else:
                    link = ""
                    media_url_type = ''
                date = datetime.strptime(post['created_time'],
                                         self.datetime_format)
                data = {'social_id': post['id'],
                        'name': 'fb fanpage %s' % post['id'],
                        'slug': 'fb_fanpage_%s' % post['id'],
                        'resource_date': date,
                        'description': post['message'],
                        'media_url': link,
                        'media_url_type': media_url_type,
                        'author': post['from']['name'],
                        }
                datas.append(data)

        return datas
