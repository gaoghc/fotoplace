import scrapy
from scrapy.selector import Selector
from fotoplace.items import FotoplaceItem
import zlib
from cookielib import CookieJar
import hmac
from hashlib import sha256
import time
from fotoplace.myconfig import UsersConfig
from datetime import datetime
import json
from fotoplace import settings

from pybloom import BloomFilter

class FotoSpider(scrapy.Spider):
    name = "fotoplacespider"
    domain = 'www.fotoplace.cc'

    secret = ''
    uid = ''

    bf = BloomFilter(capacity=10000000, error_rate=0.0001)

    headers = {
        'Client-Agent': settings.CLIENT_AGENT,
        'Accept-Language': 'en_US',
        'TimeZone': 'America/Chicago',
        'timestamp': '',
        'token': '',
        'Host': 'www.fotoplace.cc',
        'Connection': 'Keep-Alive',
        'User-Agent': 'okhttp/2.4.0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    def start_requests(self):

        localtime = time.time() + 300
        timestamp = str(int(localtime * 1000))
        key = settings.APP_KEY
        h = hmac.new(key, '', sha256)
        updateStr = settings.USER_TOKEN
        h.update(updateStr + timestamp)
        token = h.hexdigest()

        headers = self.headers
        headers['timestamp'] = timestamp
        headers['token'] = token


        yield scrapy.http.FormRequest(
            url = 'http://www.fotoplace.cc/api3/account/login/mobile?osType=android5.1.1-SonyC6806',

            headers = headers,
            formdata = {
                'countryNo': UsersConfig['countryNo'],
                'mobileNo': UsersConfig['mobileNo'],
                'password': UsersConfig['password']
            },
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': 1
            },
            callback=self.post_login,
        )


    def post_login(self, response):
        print 'hello'
        print response.headers
        print response.body

        data = json.loads(response.body_as_unicode())
        uid = data[u'data'][u'uid']
        secret = data[u'data'][u'secret']

        self.secret = secret
        self.uid = uid


        url = 'http://www.fotoplace.cc/user/api/user/25369118/followings?followingId=&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID
        localTime = time.time() + 300
        timestamp = str(int(localTime * 1000))
        h = hmac.new(str(secret), '', sha256)
        updateStr = settings.USER_TOKEN
        h.update(updateStr + timestamp+'&uid='+uid)
        token = h.hexdigest()

        headers = self.headers
        headers['timestamp'] = timestamp
        headers['token'] = token

        yield scrapy.http.Request(
            url = url,
            headers = headers,
            meta = {
                 'cookiejar': response.meta['cookiejar'],
                 'uid': uid,
            },
            callback = self.followinglist,
            dont_filter = True
        )

    def followinglist(self, response):
        print '===========following============'
        puid = response.meta.get('uid')

        followersdata = json.loads(response.body_as_unicode())
        followings = followersdata['data']['followings']
        print len(followings)

        if len(followings) == 30:
            for following in followings:
                uid = following[u'uid']
                followingId = following[u'followingId']
                print uid, followingId

                if uid in self.bf:
                    continue
                else:
                    self.bf.add(uid)

                # =============request post=============
                url = 'http://www.fotoplace.cc/user/api/user/'+uid+'/posts?postId=0&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.postlist,
                    dont_filter=True
                )

                #==========request follower list==============
                url = 'http://www.fotoplace.cc/user/api/user/'+uid+'/followers?followingId=&osType=android5.1.1-SonyC6806&uid='+self.uid


                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followerlist,
                    dont_filter=True
                )


                #===========request following list==============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/followings?followingId=&osType=android5.1.1-SonyC6806&uid=' + self.uid

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followinglist,
                    dont_filter=True
                )



            #==============continue to update the following list===================
            url = 'http://www.fotoplace.cc/user/api/user/'+ puid +'/followings?followingId='+str(followingId)+'&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

            localTime = time.time() + 300
            timestamp = str(int(localTime * 1000))
            h = hmac.new(str(self.secret), '', sha256)
            updateStr = settings.USER_TOKEN
            h.update(updateStr + timestamp + '&uid=' + self.uid)
            token = h.hexdigest()
            # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


            headers = self.headers
            headers['timestamp'] = timestamp
            headers['token'] = token

            yield scrapy.http.Request(
                url=url,
                headers=headers,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'uid': uid,
                },
                callback=self.followinglist,
                dont_filter=True
            )


        else:
            for following in followings:
                uid = following[u'uid']
                followingId = following[u'followingId']
                print uid, followingId

                if uid in self.bf:
                    continue
                else:
                    self.bf.add(uid)

                # =============request post=============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/posts?postId=0&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.postlist,
                    dont_filter=True
                )

                # ==========request follower list==============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/followers?followingId=&osType=android5.1.1-SonyC6806&uid=' + self.uid

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followerlist,
                    dont_filter=True
                )

                # ===========request following list==============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/followings?followingId=&osType=android5.1.1-SonyC6806&uid=' + self.uid

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followinglist,
                    dont_filter=True
                )


    def followerlist(self, response):
        print '===========followers============'
        puid = response.meta.get('uid')

        followersdata = json.loads(response.body_as_unicode())
        followers = followersdata['data']['followers']
        print len(followers)


        if len(followers) == 30:
            for follower in followers:
                uid = follower[u'uid']
                followerId = follower[u'followingId']
                print uid, followerId

                if uid in self.bf:
                    continue
                else:
                    self.bf.add(uid)

                #=============request post=============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/posts?postId=0&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.postlist,
                    dont_filter=True
                )

                #==========request follower list==============
                url = 'http://www.fotoplace.cc/user/api/user/'+uid+'/followers?followingId=&osType=android5.1.1-SonyC6806&uid='+self.uid


                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followerlist,
                    dont_filter=True
                )


                #===========request following list==============
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/followings?followingId=&osType=android5.1.1-SonyC6806&uid=' + self.uid

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.followinglist,
                    dont_filter=True
                )



            #==============continue to update the following list===================
            url = 'http://www.fotoplace.cc/user/api/user/'+ puid +'/followings?followingId='+str(followerId)+'&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

            localTime = time.time() + 300
            timestamp = str(int(localTime * 1000))
            h = hmac.new(str(self.secret), '', sha256)
            updateStr = settings.USER_TOKEN
            h.update(updateStr + timestamp + '&uid=' + self.uid)
            token = h.hexdigest()
            # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


            headers = self.headers
            headers['timestamp'] = timestamp
            headers['token'] = token

            yield scrapy.http.Request(
                url=url,
                headers=headers,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'uid': puid,
                },
                callback=self.followinglist,
                dont_filter=True
            )


        else:
            for follower in followers:
                uid = follower[u'uid']
                followerId = follower[u'followingId']
                print uid, followerId

                if uid in self.bf:
                    continue
                else:
                    self.bf.add(uid)

                #====================request post======================
                url = 'http://www.fotoplace.cc/user/api/user/' + uid + '/posts?postId=0&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

                localTime = time.time() + 300
                timestamp = str(int(localTime * 1000))
                h = hmac.new(str(self.secret), '', sha256)
                updateStr = settings.USER_TOKEN
                h.update(updateStr + timestamp + '&uid=' + self.uid)
                token = h.hexdigest()
                # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


                headers = self.headers
                headers['timestamp'] = timestamp
                headers['token'] = token

                yield scrapy.http.Request(
                    url=url,
                    headers=headers,
                    meta={
                        'cookiejar': response.meta['cookiejar'],
                        'uid': uid,
                    },
                    callback=self.postlist,
                    dont_filter=True
                )


    def postlist(self, response):
        print "============download post============"
        postdata = json.loads(response.body_as_unicode())
        posts = postdata['data']['posts']
        print len(posts)

        uid = response.meta['uid']


        if len(posts) == 20:
            for post in posts:
                postText = post[u'postText']
                postId = post[u'postId']
                # print '================'+uid+ '==='+ str(len(postText))+'============================================='
                if len(postText)>0:
                    item = FotoplaceItem()

                    item['postText'] = postText
                    item['postId'] = postId

                    item['bigUrl'] = post[u'bigUrl']
                    item['smallUrl'] = post[u'smallUrl']
                    item['location'] = post[u'locationAddress']
                    item['createTime'] = post[u'createTime']

                    item['likeNumber'] = post[u'likeNumber']
                    item['commentNumber'] = post[u'commentNumber']

                    print postText

                    yield item

            #================continue to request posts========================
            url = 'http://www.fotoplace.cc/user/api/user/'+ uid + '/posts?postId='+postId+'&osType=android5.1.1-SonyC6806&uid='+settings.USER_ID

            localTime = time.time() + 300
            timestamp = str(int(localTime * 1000))
            h = hmac.new(str(self.secret), '', sha256)
            updateStr = settings.USER_TOKEN
            h.update(updateStr + timestamp + '&uid=' + self.uid)
            token = h.hexdigest()
            # print datetime.fromtimestamp(localTime).strftime('%Y-%m-%d %H:%M:%S.%f')


            headers = self.headers
            headers['timestamp'] = timestamp
            headers['token'] = token

            yield scrapy.http.Request(
                url=url,
                headers=headers,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'uid': uid,
                },
                callback=self.postlist,
                dont_filter=True
            )

        else:
            for post in posts:
                postText = post[u'postText']
                postId = post[u'postId']
                # print '================'+uid+ '==='+ str(len(postText))+'============================================='
                if len(postText)>0:
                    item = FotoplaceItem()

                    item['postText'] = postText
                    item['postId'] = postId

                    item['bigUrl'] = post[u'bigUrl']
                    item['smallUrl'] = post[u'smallUrl']
                    item['location'] = post[u'locationAddress']
                    item['createTime'] = post[u'createTime']

                    item['likeNumber'] = post[u'likeNumber']
                    item['commentNumber'] = post[u'commentNumber']

                    print postText

                    yield item










