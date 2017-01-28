# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from fotoplace import settings

import urllib
import os
import json
import codecs

class FotoplacePipeline(object):
    def process_item(self, item, spider):

        dir_path = '%s/%s' % (settings.IMAGES_STORE, spider.name)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # print "================enter pipeline====================================="
        img_url = item['bigUrl']
        # img_url = item['smallUrl']
        list_name = img_url.split('/')
        file_name = list_name[len(list_name)-1]
        file_name = file_name.split('-')
        file_name = file_name[0]

        file_path = '%s/%s' % (dir_path, file_name)


        urllib.urlretrieve(img_url, file_path)

        data = {
            'postText': item['postText'],
            'postId': item['postId'],
            'bigUrl': item['bigUrl'],
            'smallUrl': item['smallUrl'],
            'location': item['location'],
            'createTime': item['createTime'],
            'likeNumber': item['likeNumber'],
            'commentNumber': item['commentNumber'],
            'filename': file_name,
        }

        # Writing JSON data
        with open('data.json', 'a') as f:
            json.dump(data, f)
            f.write('\n')

        return item
