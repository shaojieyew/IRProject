import twitter
import requests, base64
import oauth2 as oauth2
import json
import pysolr,json,argparse

# Create your views here.
class Tweet_api:
    def __init__(self, *args):
        self.data = args
    def getTweet(object):
        string = '%s:%s' % ('ly1IqoOFEF6vxnMCNEDu9HfgJ','rh0z1LMkAitP4CFzxNpRnrIMJYHlfvZwk1r1QGdyl2lrIDjqMY')
        base64string  = base64.standard_b64encode(string.encode('utf-8'))
        response = requests.post("https://api.twitter.com/oauth2/token",
            headers={
            "Authorization": "Basic %s" % base64string.decode('utf-8'),
            "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"},
            data={
            "grant_type": "client_credentials"}
            )
        token_json = response.json()
        access_token = token_json['access_token']
        response = requests.get("https://api.twitter.com/1.1/search/tweets.json?q=%23cryptocoin",
            headers={"Authorization": "Bearer %s" % access_token})
        rep = response.json()
        rep = rep['statuses']
        return rep


        
