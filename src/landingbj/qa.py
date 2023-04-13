#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# qa.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#


# cython: language_level=3
import argparse
import json
import logging
import random
from io import BytesIO

import requests
import zeep
from PIL import Image
from requests import HTTPError
from zeep import Settings

from landingbj.config import Config

SASS_BASE_URL = 'http://saas.landingbj.com'
KGRAPH_BASE_URL = 'http://kgraph.landingbj.com'

# SASS_BASE_URL = 'http://localhost:8080'
# KGRAPH_BASE_URL = 'http://localhost:8080/migrate'

rpa_task_url = SASS_BASE_URL + '/getTaskByChannelName'
rpa_task_image_url = SASS_BASE_URL + '/getRpaTaskImage'
repeater_contact_url = SASS_BASE_URL + '/getRepeaterContact'
repeater_task_url = SASS_BASE_URL + '/getRepeaterTask'
add_repeater_message_url = SASS_BASE_URL + '/addRepeaterMessage'
ai_wsdl = 'http://ai.landingbj.com/KnowledgeService?wsdl'

get_qa_list_url = KGRAPH_BASE_URL + '/search/getQaList'
delete_qa_detail_url = KGRAPH_BASE_URL + '/search/appDeleteQaDetail'
add_qa_detail_url = KGRAPH_BASE_URL + '/search/addQaDetail'
update_qa_detail_url = KGRAPH_BASE_URL + '/search/updateOneQaDetail'

get_rpa_contact_url = SASS_BASE_URL + '/getRpaContact'
get_timer_url = SASS_BASE_URL + '/getTaskList'
get_app_type_list_url = SASS_BASE_URL + '/getAppTypeList'
get_channel_id_by_name_url = SASS_BASE_URL + '/getChannelIdByName'
add_app_contact_url = SASS_BASE_URL + '/addAppContact'
add_timer_task_url = SASS_BASE_URL + '/addRpaTask'
update_timer_task_url = SASS_BASE_URL + '/updateTimerTask'
delete_timer_task_url = SASS_BASE_URL + '/appDeleteRpaTask'
add_repeater_url = SASS_BASE_URL + '/addRpaRepeater'
update_repeater_url = SASS_BASE_URL + '/updateRepeater'
delete_repeater_url = SASS_BASE_URL + '/appDeleteRepeater'
add_app_keyword_url = SASS_BASE_URL + '/addAppKeyword'
delete_app_contact_url = SASS_BASE_URL + '/deleteAppContact'
update_app_contact_url = SASS_BASE_URL + '/updateAppContact'
add_black_list_url = SASS_BASE_URL + '/addBlackList'
get_unfollowed_tikTok_id_url = SASS_BASE_URL + '/getUnfollowedTikTokId'
get_unfollowed_info_url = SASS_BASE_URL + '/getUnfollowedInfo'
set_app_followed_url = SASS_BASE_URL + '/setAppFollowed'


def add_black_list(app_id, user_id):
    query = {'appId': app_id, 'userId': user_id}
    response = requests.post(add_black_list_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def qa_call(question, category, channel_user):
    result = ''
    settings = Settings(extra_http_headers={'channel_user': channel_user.encode('utf-8')})
    try:
        client = zeep.Client(wsdl=ai_wsdl, settings=settings)
        result = client.service.questionAnswer(question.strip(), category). \
            replace('<QuestionResult>', '', 1).replace('</QuestionResult>', '', 1)
    except HTTPError as e:
        logging.exception("message")
    return result


def get_rpa_task(channel_name, app_id, channel_user):
    query = {'channelName': channel_name, 'appId': app_id, 'channelUser': channel_user}
    try:
        response = requests.get(rpa_task_url, params=query)
    except Exception as e:
        return None, None, None
    y = response.json()
    if y['status'] == 'unauthorized':
        Config.default_flag = True
        return None, None, None
    else:
        Config.default_flag = False
    if y['status'] == 'failed':
        return None, None, None
    return y['data']['contactNameList'], y['data']['message'], y['data']['images']


def get_rpa_task_image(channel_name, image_name, channel_user):
    query = {'channelName': channel_name, 'imageName': image_name, 'channelUser': channel_user}
    r = requests.post(rpa_task_image_url, data=query)
    image = Image.open(BytesIO(r.content))
    return image


def get_repeater_contact(channel_name, app_id, channel_user):
    query = {'channelName': channel_name, 'appId': app_id, 'channelUser': channel_user}
    response = requests.get(repeater_contact_url, params=query)
    if response.status_code != 200:
        return []
    y = response.json()
    if y['status'] == 'unauthorized':
        Config.default_flag = True
        return []
    else:
        Config.default_flag = False
    if y['status'] == 'failed':
        return []
    return y['data']


def get_repeater_task(channel_name, app_id, channel_user):
    query = {'channelName': channel_name, 'appId': app_id, 'channelUser': channel_user}
    try:
        response = requests.get(repeater_task_url, params=query)
    except Exception as e:
        return None, None
    y = response.json()
    if y['status'] == 'unauthorized':
        Config.default_flag = True
        return None, None
    else:
        Config.default_flag = False
    if y['status'] == 'failed':
        return None, None
    return y['data']['contactNameList'], y['data']['message']


def add_repeater_message(message_dict):
    response = requests.post(add_repeater_message_url, data=message_dict,
                             headers={'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'})
    y = response.json()
    return y['status']


def get_image_by_url(url):
    return Image.open(requests.get(url, stream=True, timeout=2).raw)


def get_qa_list(qa_data_page, qa_data_page_size):
    query = {'pageNumber': qa_data_page, 'pageSize': qa_data_page_size, 'category': Config.channel_name}
    response = requests.get(get_qa_list_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def get_timer_list():
    query = {'channelId': get_channel_id_by_name()}
    response = requests.request("GET", get_timer_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def get_repeater_list():
    query = {'channelId': get_channel_id_by_name()}
    get_repeater_url = SASS_BASE_URL + '/getRepeaterList'
    response = requests.request("GET", get_repeater_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def delete_qa_detail(qid):
    params = {'id': qid}
    response = requests.post(delete_qa_detail_url, params=params)
    y = response.json()
    return y


def add_qa_detail(data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(add_qa_detail_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def update_qa_detail(data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(update_qa_detail_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def add_app_contact(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.post(add_app_contact_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def update_app_contact(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.post(update_app_contact_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def delete_app_contact(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.post(delete_app_contact_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def get_rpa_contact(app_id):
    query = {'channelId': get_channel_id_by_name(), 'appId': app_id}
    response = requests.request("GET", get_rpa_contact_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def get_keyword_list():
    query = {'channelId': get_channel_id_by_name()}
    get_keyword_url = SASS_BASE_URL + '/getKeywordList'
    response = requests.request("GET", get_keyword_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


app_type = {}
channel_id_cache = {}


def get_app_type_list():
    if len(app_type) > 0:
        return app_type
    query = {'channelId': get_channel_id_by_name(), 'username': Config.channel_name}
    response = requests.request("GET", get_app_type_list_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()

    for a in y['data']:
        app_type[a['appName']] = a['appId']
    return app_type


def get_channel_id_by_name():
    channel_name = Config.channel_name
    if channel_name in channel_id_cache:
        return channel_id_cache[channel_name]
    query = {'channelName': channel_name}
    response = requests.request("GET", get_channel_id_by_name_url, params=query)
    y = response.json()
    channel_id_cache[channel_name] = y['channelId']
    return y['channelId']


def add_timer_task(data, image_files):
    data['channelId'] = get_channel_id_by_name()
    files = []
    if len(image_files) > 0:
        for image_file in image_files:
            files.append(('image_upload', open(image_file, 'rb')))
    else:
        files = {'image_upload': (None, 'content')}
    response = requests.request("POST", add_timer_task_url, data=data, files=files)
    y = response.json()
    return y


def update_timer_task(data, image_files):
    data['channelId'] = get_channel_id_by_name()
    files = []
    if len(image_files) > 0:
        for image_file in image_files:
            files.append(('image_upload', open(image_file, 'rb')))
    else:
        files = {'image_upload': (None, 'content')}
    response = requests.request("POST", update_timer_task_url, data=data, files=files)
    y = response.json()
    return y


def delete_timer_task(data_id):
    params = {'taskIds': data_id}
    response = requests.post(delete_timer_task_url, params=params)
    y = response.json()
    return y


def add_repeater(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.request("POST", add_repeater_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def update_repeater(data):
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", update_repeater_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def delete_repeater(data_id):
    params = {'repeaterIds': data_id}
    response = requests.post(delete_repeater_url, params=params)
    y = response.json()
    return y


def add_app_keyword(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.post(add_app_keyword_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def login(data):
    headers = {'Content-Type': 'application/json'}
    login_by_name_url = SASS_BASE_URL + '/loginByName'
    response = requests.post(login_by_name_url, headers=headers, data=json.dumps(data))
    y = response.json()
    return y


def get_user_role(data):
    headers = {'Content-Type': 'application/json'}
    get_role_by_name_url = SASS_BASE_URL + '/getRoleByName'
    response = requests.post(get_role_by_name_url, headers=headers, data=json.dumps(data))
    y = response.json()
    if y['status'] == 'success':
        return y['data']
    return 0


get_rpa_guide_list_url = SASS_BASE_URL + '/getRpaGuideList'
add_guide_info_url = SASS_BASE_URL + '/addGuideInfo'


def add_rpa_guide(data):
    headers = {'Content-Type': 'application/json'}
    data['channelId'] = get_channel_id_by_name()
    response = requests.request("POST", add_guide_info_url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def get_guide_list():
    query = {'channelId': get_channel_id_by_name()}
    response = requests.request("GET", get_rpa_guide_list_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    if y['status'] == 'success':
        result = {}
        for i in y['data']:
            result[(i['appName'], i['type'])] = i
        return result
    return None


def add_black_list(app_id, user_id):
    query = {'appId': app_id, 'userId': user_id}
    response = requests.post(add_black_list_url, params=query)
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def set_app_followed(source, target):
    headers = {'Content-Type': 'application/json'}
    data = {'source': source, 'target': target}
    response = requests.request("POST", set_app_followed_url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        return None
    y = response.json()
    return y


def get_unfollowed_tikTok_id(tiktok_id):
    query = {'tiktokId': tiktok_id}
    try:
        response = requests.get(get_unfollowed_tikTok_id_url, params=query)
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return None
    if response.status_code != 200:
        return None
    y = response.json()
    if y['status'] == 'failed':
        return None
    return y['data']


def get_unfollowed_info(app_id, follow_info):
    query = {'appId': app_id, 'followInfo': follow_info}
    try:
        response = requests.get(get_unfollowed_info_url, params=query)
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return None
    if response.status_code != 200:
        return None
    y = response.json()
    if y['status'] == 'failed':
        return None
    return y['data']


post_text_path = "http://127.0.0.1:8000/txt2img"
get_img_path = "http://127.0.0.1:8000/get_image"


def get_image(prompt: str = ''):
    headers = {'Content-Type': 'application/json'}
    params = {"prompt": prompt,
              "steps": 2,
              "plms": False,
              "dpm": False,
              "fixed_code": False,
              "ddim_eta": 0.0,
              "n_iter": 1,
              "H": 512,
              "W": 512,
              "C": 4,
              "f": 8,
              "n_samples": 1,
              "n_rows": 1,
              "scale": 9.0,
              "from_file": None,
              "ckpt": None,
              "seed": None,
              "precision": 'full',
              "repeat": 1,
              "torchscript": False,
              "ipex": False,
              "bf16": False, }
    try:
        response = requests.request("POST", post_text_path, headers=headers, json=params)
        print(response)
        if response.status_code != 200:
            return "send txt failed"
        y = response.json()
    except Exception as e:
        print(e)
        return {'status': 'fialed to post the prompt'}
    if y:
        print(f"返回图片路径{type(y)} {y}")
        try:
            data = {"image_path": y.get("result", " ")}
            response = requests.get(get_img_path, params=data)
            print(f"send path status{response.status_code}")
        except Exception as e:
            return "fialed to get the image path"
        if response.status_code != 200:
            return None
        content = response.content
        print(f"返回图片文件{content} \n 类型{type(content)}")
        return content


if __name__ == '__main__':
    qs = ['今天拍发货吗', '后天能到吗', '你们地址发我，我寄给你们吗', '麻烦了', '实在不好意思我没注意', '那老客户还是原价', '亲请问快递送到哪里了',
          '麻烦您备注一下', '我今天买什么时候到什么时候发货', '这么晚呀', '问了好久都没人说话，你们还发货吗', '不要发申通快递哟', '只要不是申通快递其他都可以', '这两种什么区别']
    c = 'qa'

    get_guide_list()
