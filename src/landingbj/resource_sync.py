#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# resource_sync.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#


# cython: language_level=3
import logging
import os
import time
import urllib
from pathlib import Path
from threading import Thread

import requests

from landingbj.config import Config

get_rpa_image_url = 'http://saas.landingbj.com/share/image'
get_rpa_image_list_url = 'http://saas.landingbj.com/getRpaImageList'


class ResourceSync(Thread):
    def __init__(self):
        super(ResourceSync, self).__init__()

    def run(self):
        image_list = self.get_image_to_update()
        for image_name in image_list:
            image_name_path = Path(Config.image_app_dir + "/" + image_name)
            app_dir = image_name_path.parent
            image = self.get_remote_image(image_name)
            if not os.path.exists(app_dir):
                os.makedirs(app_dir)
            f = open(image_name_path, 'wb')
            f.write(image)
            f.close()
            logging.info('update image: %s' % image_name)

    def get_image_to_update(self):
        result = []
        query = {}
        try:
            response = requests.get(get_rpa_image_list_url, params=query)
        except Exception as e:
            return result
        y = response.json()
        for image in y:
            local_image = Config.image_app_dir + image
            if 'tiktok' in local_image or 'kuaishou' in local_image:
                continue
            if not os.path.isfile(local_image):
                result.append(image)
                continue
            size = os.path.getsize(local_image)
            if size != y[image]:
                result.append(image)
        return result

    def get_remote_image(self, image_name):
        url = get_rpa_image_url + '/' + image_name
        image = requests.get(url).content
        return image
