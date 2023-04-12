# cython: language_level=3
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path
from random import randrange
from threading import Thread

import numpy as np
import pyautogui
import pyperclip

from landingbj import util, autogui
from landingbj.agent_browser import AgentBrowser
from landingbj.agent_config import AgentConfig, remove_browser_tab, add_browser_tab, rel_to_abs_pos
from landingbj.config import Config
from landingbj.qa import qa_call, add_app_contact, add_black_list, get_unfollowed_info, set_app_followed
from landingbj.util import LRUCache, wait_until_either_show


class SocialConfig:
    abort = False

    qq_people_tab_rel_x, qq_people_tab_rel_y = 215, 38
    qq_people_search_rel_x, qq_people_search_rel_y = 192, 94
    qq_service_tab_rel_x, qq_service_tab_rel_y = 677, 38
    qq_service_search_rel_x, qq_service_search_rel_y = 324, 102

    qq_contact_region = AgentConfig.qq_contact_region
    qq_people_tab_x = qq_contact_region[0] + qq_people_tab_rel_x
    qq_people_tab_y = qq_contact_region[1] + qq_people_tab_rel_y
    qq_people_search_x = qq_contact_region[0] + qq_people_search_rel_x
    qq_people_search_y = qq_contact_region[1] + qq_people_search_rel_y
    qq_service_tab_x = qq_contact_region[0] + qq_service_tab_rel_x
    qq_service_tab_y = qq_contact_region[1] + qq_service_tab_rel_y
    qq_service_search_x = qq_contact_region[0] + qq_service_search_rel_x
    qq_service_search_y = qq_contact_region[1] + qq_service_search_rel_y
    qq_search_sample_region = (qq_contact_region[0] + 46, qq_contact_region[1] + 215, 30, 30)
    show_online_checkbox_x = qq_contact_region[0] + 659
    show_online_checkbox_y = qq_contact_region[1] + 163

    browser_bar_height = 0
    tiktok_search_rel_x, tiktok_search_rel_y = 394, 107 - browser_bar_height
    tiktok_video_stop_rel_x, tiktok_video_stop_rel_y = 500, 500 - browser_bar_height

    tiktok_contact_region = None
    tiktok_search_x = 0 + tiktok_search_rel_x
    tiktok_search_y = 0 + tiktok_search_rel_y
    tiktok_video_stop_x = 0 + tiktok_video_stop_rel_x
    tiktok_video_stop_y = 0 + tiktok_video_stop_rel_y

    kuaishou_search_rel_x, kuaishou_search_rel_y = 881, 115
    kuaishou_search_x = AgentConfig.chrome_window_xy[0] + kuaishou_search_rel_x
    kuaishou_search_y = AgentConfig.chrome_window_xy[1] + kuaishou_search_rel_y
    kuaishou_video_x, kuaishou_video_y = AgentConfig.chrome_window_xy[0] + 178, AgentConfig.chrome_window_xy[1] + 434

    comment_reply = {}
    tiktok_id = None
    kuaishou_id = None
    kuaishou_profile_url = None

    @classmethod
    def set_tiktok_contact_pos(cls, tiktok_contact_region):
        SocialConfig.tiktok_contact_region = tiktok_contact_region
        SocialConfig.tiktok_search_x = tiktok_contact_region[0] + SocialConfig.tiktok_search_rel_x
        SocialConfig.tiktok_search_y = tiktok_contact_region[1] + SocialConfig.tiktok_search_rel_y
        SocialConfig.tiktok_video_stop_x = tiktok_contact_region[0] + SocialConfig.tiktok_video_stop_rel_x
        SocialConfig.tiktok_video_stop_y = tiktok_contact_region[1] + SocialConfig.tiktok_video_stop_rel_y
        AgentConfig.tiktok_avatar_pos = rel_to_abs_pos(tiktok_contact_region, AgentConfig.tiktok_avatar_pos)

    @classmethod
    def set_qq_contact_pos(cls, qq_contact_region):
        cls.qq_contact_region = qq_contact_region
        cls.qq_people_tab_x = qq_contact_region[0] + cls.qq_people_tab_rel_x
        cls.qq_people_tab_y = qq_contact_region[1] + cls.qq_people_tab_rel_y
        cls.qq_people_search_x = qq_contact_region[0] + cls.qq_people_search_rel_x
        cls.qq_people_search_y = qq_contact_region[1] + cls.qq_people_search_rel_y
        cls.qq_service_tab_x = qq_contact_region[0] + cls.qq_service_tab_rel_x
        cls.qq_service_tab_y = qq_contact_region[1] + cls.qq_service_tab_rel_y
        cls.qq_service_search_x = qq_contact_region[0] + cls.qq_service_search_rel_x
        cls.qq_service_search_y = qq_contact_region[1] + cls.qq_service_search_rel_y
        cls.qq_search_sample_region = (qq_contact_region[0] + 46, qq_contact_region[1] + 215, 30, 30)
        cls.show_online_checkbox_x = qq_contact_region[0] + 659
        cls.show_online_checkbox_y = qq_contact_region[1] + 163


def auto_func(func, *args, **kwargs):
    if SocialConfig.abort:
        return
    func(*args, **kwargs)


def close_current_tab():
    url = AgentBrowser.get_browser_url()
    logging.info('关闭tab地址: ' + url)
    auto_func(pyautogui.hotkey, 'ctrl', 'w')
    time.sleep(2)


tiktok_cache = LRUCache(1000)
kuaishou_cache = LRUCache(1000)
url_cache = LRUCache(10000)
tiktok_url_cache = LRUCache(100000)
kuaishou_url_cache = LRUCache(100000)


def load_url_cache(cache, app_type, app_user):
    if app_user is None:
        return
    cache_file_name = app_type + '_' + Config.channel_name + '_' + app_user + '.log'
    cache_file_path = Path(AgentConfig.guide_url_tmp_dir + '/' + cache_file_name)
    cache_file_path.touch(exist_ok=True)
    with open(cache_file_path, encoding='utf-8') as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            str_list = line.split(',', maxsplit=1)
            if len(str_list) == 2:
                timestamp, url = str_list
                if url.startswith('http'):
                    cache.put(url, timestamp)


class TiktokRpaProcess:
    def __init__(self, search_keyword, reply_keyword, tiktok_search_idx):
        self.reply_keyword = reply_keyword
        self.search_keyword = search_keyword
        self.tiktok_search_idx = tiktok_search_idx
        self.browser_tab = AgentConfig.browser_tab[Config.app_type_tiktok]
        # self.browser_tab = [0]

    @classmethod
    def get_tiktok_id(cls):
        # AgentBrowser.change_browser_tab(AgentConfig.browser_tab[Config.app_type_tiktok][0])
        x, y = AgentConfig.tiktok_avatar_pos
        auto_func(pyautogui.click, x, y)
        time.sleep(3)
        # add_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][0] + 1)
        x, y = AgentConfig.tiktok_id_pos
        auto_func(pyautogui.click, x, y, clicks=2)
        time.sleep(0.5)
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.5)
        # remove_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][1])
        tiktok_id = pyperclip.paste()
        close_current_tab()
        return tiktok_id

    @classmethod
    def follow_each_other(cls, tiktok_id):
        if tiktok_id is None:
            return
        AgentBrowser.change_browser_tab(AgentConfig.browser_tab[Config.app_type_tiktok][0])
        pyperclip.copy(tiktok_id)
        auto_func(pyautogui.click, SocialConfig.tiktok_search_x, SocialConfig.tiktok_search_y)
        time.sleep(0.2)
        auto_func(pyautogui.hotkey, 'ctrl', 'a')
        auto_func(pyautogui.hotkey, 'backspace')
        auto_func(pyautogui.hotkey, 'ctrl', 'v')
        auto_func(pyautogui.hotkey, 'enter')
        # add_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][0] + 1, override=True)
        # AgentBrowser.crack_tiktok_code(sleep_time=3)
        # AgentConfig.browser_tab[Config.app_type_tiktok].insert(1, 2)
        tiktok_follow = Config.tiktok_follow[0]
        tiktok_unfollow = Config.tiktok_unfollow[0]
        wait_until_either_show(tiktok_follow, tiktok_unfollow, region=AgentConfig.tiktok_search_follow_region, max_count=20)
        pos = pyautogui.locateCenterOnScreen(tiktok_follow, region=AgentConfig.tiktok_search_follow_region)
        if pos is not None:
            auto_func(pyautogui.click, pos.x, pos.y)
            time.sleep(2)
            auto_func(pyautogui.hotkey, 'f5')
            wait_until_either_show(tiktok_follow, tiktok_unfollow, region=AgentConfig.tiktok_search_follow_region,
                                   max_count=20)
            pos = pyautogui.locateCenterOnScreen(tiktok_follow, region=AgentConfig.tiktok_search_follow_region)
            if pos is not None:
                logging.info('你在关注用户' + tiktok_id + '时，被加入互关黑名单')
                # add_black_list(Config.app_type_dict[Config.app_type_tiktok], tiktok_id)
            else:
                logging.info('你已关注用户' + tiktok_id)
                set_app_followed(SocialConfig.tiktok_id, tiktok_id)
        else:
            logging.info(tiktok_id + '用户已经被你关注')
            set_app_followed(SocialConfig.tiktok_id, tiktok_id)
        # remove_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][1])
        close_current_tab()

    def search_action(self):
        pyperclip.copy(self.search_keyword)
        time.sleep(0.2)
        auto_func(pyautogui.click, SocialConfig.tiktok_search_x, SocialConfig.tiktok_search_y)
        time.sleep(0.2)
        auto_func(pyautogui.hotkey, 'ctrl', 'a')
        time.sleep(0.1)
        auto_func(pyautogui.hotkey, 'backspace')
        time.sleep(0.1)
        auto_func(pyautogui.hotkey, 'ctrl', 'v')
        time.sleep(0.2)
        auto_func(pyautogui.hotkey, 'enter')
        time.sleep(3)
        x, y = AgentConfig.tiktok_video_tab_pos
        auto_func(pyautogui.click, x=x, y=y)
        self.search_filter()

    def search(self):
        if len(self.browser_tab) == 1:
            AgentBrowser.change_browser_tab(str(self.browser_tab[0]))
            # AgentBrowser.crack_tiktok_code(sleep_time=3)
            self.search_action()
            add_browser_tab(Config.app_type_tiktok, 2)
            # self.browser_tab.append(self.browser_tab[0] + 1)
            self.tiktok_search_idx['keyword_idx'] = self.tiktok_search_idx['keyword_idx'] + 1
            # AgentBrowser.crack_tiktok_code(sleep_time=3)

        if len(self.browser_tab) == 2:
            AgentBrowser.change_browser_tab(str(self.browser_tab[1]))
            tiktok_video_search = Config.tiktok_video_search[0]
            util.wait_until_object_show(tiktok_video_search, (382, 211, 90, 830), 20)
            pos_list = autogui.locateAllOnScreen(tiktok_video_search, region=(382, 211, 984, 830))

            count = 0
            while len(pos_list) == 0 and count < 3:
                auto_func(pyautogui.hotkey, 'f5')
                util.wait_until_object_show(tiktok_video_search, (382, 211, 90, 830), 20)
                pos_list = autogui.locateAllOnScreen(tiktok_video_search, region=(382, 211, 984, 830))
                count = count + 1
                if len(pos_list) == 0 and count < 3:
                    time.sleep(5)
                
            if len(pos_list) == 0:
                close_current_tab()
                remove_browser_tab(Config.app_type_tiktok, self.browser_tab[1])
                self.tiktok_search_idx['video_idx'] = AgentConfig.guide_wait_max_count
                # self.browser_tab.pop()
                return
            if self.tiktok_search_idx['video_idx'] >= len(pos_list):
                tiktok_bottom = Config.tiktok_bottom[0]
                finish_region = (604, 886, 100, 100)
                is_finished = autogui.locateOnScreen(tiktok_bottom, region=finish_region)
                if is_finished:
                    close_current_tab()
                    remove_browser_tab(Config.app_type_tiktok, self.browser_tab[1])
                    self.tiktok_search_idx['video_idx'] = AgentConfig.guide_wait_max_count
                    return
                x, y = pyautogui.center(pos_list[0])
                auto_func(pyautogui.moveTo, x, y)
                time.sleep(0.3)
                auto_func(pyautogui.scroll, -1080)
                self.tiktok_search_idx['video_idx'] = 0
                time.sleep(3)
                return
            pos = pos_list[self.tiktok_search_idx['video_idx']]
            x, y = pyautogui.center(pos)
            if y - AgentConfig.chrome_window_xy[1] < 400:
                self.tiktok_search_idx['video_idx'] = self.tiktok_search_idx['video_idx'] + 1
                return
            auto_func(pyautogui.click, x=x - 104, y=y - 134)
            # AgentBrowser.crack_tiktok_code(sleep_time=3)
            add_browser_tab(Config.app_type_tiktok, 3)
            # self.browser_tab.append(self.browser_tab[1] + 1)
            time.sleep(3)
            url = AgentBrowser.get_browser_url()
            # AgentBrowser.rpa_log(Config.app_type_tiktok, '视频地址: ' + AgentBrowser.get_browser_url())
            logging.info('视频地址: ' + url)
            if tiktok_url_cache.get(url) is not None:
                close_current_tab()
                self.tiktok_search_idx['video_idx'] = self.tiktok_search_idx['video_idx'] + 1
                remove_browser_tab(Config.app_type_tiktok, self.browser_tab[2])
                logging.info('重复地址已跳过: ' + url)
                # self.browser_tab.pop()
                return
            else:
                tiktok_url_cache.put(url, str(datetime.now().timestamp()))
                if SocialConfig.tiktok_id is not None:
                    cache_file_name = 'tiktok' + '_' + Config.channel_name + '_' + SocialConfig.tiktok_id + '.log'
                    AgentBrowser.append_url_cache(cache_file_name, url)
            self.view_video()
            self.follow_author()
            self.like_video()
            auto_func(pyautogui.scroll, -1080)
            time.sleep(1)
            tiktok_cache.clear()
        self.like_reply_batch()

    def follow_author(self):
        if self.check_fans_status() and randrange(10) < 3:
            pos = pyautogui.center(AgentConfig.tiktok_author_follow_region)
            auto_func(pyautogui.click, pos.x, pos.y)
            time.sleep(0.5)
            # AgentBrowser.rpa_log(Config.app_type_tiktok, '关注操作完成')
            logging.info('关注操作完成')

    def view_video(self):
        x, y = AgentConfig.chrome_window_xy[0] + random.randint(675, 1075), AgentConfig.chrome_window_xy[1] + 821
        auto_func(pyautogui.moveTo, x, y)
        time.sleep(0.3)
        auto_func(pyautogui.click, x, y)
        time.sleep(3)
        auto_func(pyautogui.click, x, y - 400)
        time.sleep(0.3)

    def like_video(self):
        tiktok_like_image = Config.tiktok_like_image[0]
        util.wait_until_object_show(tiktok_like_image, (152, 854, 100, 150), 5)
        pos = autogui.locateOnScreen(tiktok_like_image, region=(152, 854, 100, 150))
        if pos is None:
            return
        x, y = pyautogui.center(pos)
        auto_func(pyautogui.moveTo, x, y)
        auto_func(pyautogui.drag, 70, 0, 0.5, button='left')
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.5)
        like_number = pyperclip.paste()
        if like_number is not None:
            like_number = like_number.strip()
            # AgentBrowser.rpa_log(Config.app_type_tiktok, '视频点赞数: ' + like_number)
            logging.info('视频点赞数: ' + like_number)
            if like_number.isnumeric() and int(like_number) < AgentConfig.tiktok_video_like_max:
                auto_func(pyautogui.click, x, y)
                # AgentBrowser.rpa_log(Config.app_type_tiktok, '视频点赞操作完成')
                logging.info('视频点赞操作完成')

    def check_fans_status(self):
        tiktok_follow = Config.tiktok_follow[0]
        flag = pyautogui.locateOnScreen(tiktok_follow, region=AgentConfig.tiktok_author_follow_region)
        if flag is None:
            return False
        x, y = AgentConfig.tiktok_author_fan_pos
        auto_func(pyautogui.click, x, y, clicks=2)
        time.sleep(0.5)
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.5)
        fan_number = pyperclip.paste()
        if fan_number is not None:
            fan_number = fan_number.strip()
            # AgentBrowser.rpa_log(Config.app_type_tiktok, '用户粉丝数: ' + fan_number)
            logging.info('用户粉丝数: ' + fan_number)
            if fan_number.isnumeric():
                if int(fan_number) < AgentConfig.tiktok_author_fan_max:
                    return True
        return False

    def search_filter(self):
        x, y = AgentConfig.tiktok_search_filter_btn_pos
        auto_func(pyautogui.click, x, y)
        time.sleep(0.5)
        x, y = AgentConfig.tiktok_search_filter_sort_pos
        auto_func(pyautogui.click, x, y)
        time.sleep(0.1)
        x, y = AgentConfig.tiktok_search_filter_time_pos
        auto_func(pyautogui.click, x, y)
        x, y = AgentConfig.tiktok_search_filter_btn_pos
        auto_func(pyautogui.click, x, y)

    def like_reply_batch(self):
        AgentBrowser.change_browser_tab(str(self.browser_tab[2]))
        tiktok_reply = Config.tiktok_reply[0]
        tiktok_bottom = Config.tiktok_bottom[0]
        finish_region = (604, 886, 100, 100)
        is_finished = autogui.locateOnScreen(tiktok_bottom, region=finish_region)
        region = (AgentConfig.chrome_window_xy[0] + 250, AgentConfig.chrome_window_xy[1] + 130, 30, 1030)

        if is_finished is not None:
            if autogui.locateOnScreen(tiktok_reply, region=region) is not None:
                pos_list = autogui.locateAllOnScreen(tiktok_reply, region=region)
            else:
                pos_list = []
            if len(pos_list) >= 1:
                for pos in reversed(pos_list[1:]):
                    x, y = pyautogui.center(pos)
                    self.like_reply(x, y)
                    time.sleep(2)
                x, y = pyautogui.center(pos_list[0])
                pyautogui.click(x + 40, y)
                auto_func(pyautogui.scroll, -1080)
                time.sleep(1)

        count = 0
        while is_finished is None and count < 2:
            if SocialConfig.abort:
                return
            if autogui.locateOnScreen(tiktok_reply, region=region) is not None:
                pos_list = autogui.locateAllOnScreen(tiktok_reply, region=region)
            else:
                pos_list = []
            if len(pos_list) == 0 or AgentConfig.tiktok_current_reply >= AgentConfig.tiktok_max_reply:
                is_finished = True
            else:
                if len(pos_list) >= 1:
                    if AgentConfig.tiktok_current_count <= 3:
                        for pos in reversed(pos_list[1:]):
                            x, y = pyautogui.center(pos)
                            self.like_reply(x, y)
                            time.sleep(2)
                    x, y = pyautogui.center(pos_list[0])
                    pyautogui.click(x + 40, y)
                    auto_func(pyautogui.scroll, -1080)
                    time.sleep(1)
                is_finished = autogui.locateOnScreen(tiktok_bottom, region=finish_region)
                count = count + 1

        if is_finished is not None:
            AgentConfig.tiktok_current_reply = 0
            close_current_tab()
            self.tiktok_search_idx['video_idx'] = self.tiktok_search_idx['video_idx'] + 1
            remove_browser_tab(Config.app_type_tiktok, self.browser_tab[2])
            # self.browser_tab.pop()

    def at_sign_exists(self, x, y):
        region = (x - 61, y - 51, 81, 36)
        icon = Config.tiktok_at_sign[0]
        result = autogui.locateOnScreen(icon, region=region, threshold=0.9)
        if result is None:
            return False
        return True

    def like_reply(self, x, y):
        if self.at_sign_exists(x, y):
            logging.info('发现@符号，跳过该评论')
            return
        if not autogui.click_if_not_link(x, y - 34, clicks=3):
            logging.info('不是文字内容，跳过该评论')
            return
        time.sleep(0.2)
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.2)
        comment = pyperclip.paste()
        if comment is not None:
            comment = comment.strip()
        if tiktok_cache.get(comment) is not None or len(comment) == 0:
            return
        else:
            tiktok_cache.put(comment, '')
        reply = self.get_reply(comment)

        # AgentBrowser.rpa_log(Config.app_type_tiktok, '评论: ' + comment)
        logging.info('评论: ' + comment)
        if reply is not None:
            auto_func(pyautogui.click, x - 44, y)
            time.sleep(2)
            reply = reply.strip()
            # AgentBrowser.rpa_log(Config.app_type_tiktok, '回复: ' + reply)
            logging.info('回复: ' + reply)
            pyperclip.copy(reply)
            auto_func(pyautogui.click, x, y)
            time.sleep(0.2)
            auto_func(pyautogui.hotkey, 'ctrl', 'v')
            auto_func(pyautogui.hotkey, 'enter')
            AgentConfig.tiktok_current_count = AgentConfig.tiktok_current_count + 1
        else:
            AgentConfig.tiktok_current_count = 0
        AgentConfig.tiktok_current_reply = AgentConfig.tiktok_current_reply + 1

    def get_reply(self, comment):
        for s in self.reply_keyword:
            if s in comment:
                answer = qa_call(comment, Config.channel_name, Config.channel_user)
                if len(answer) == 0:
                    return None
                return answer
        comment = re.sub(r'[\(\[].*?[\)\]]', '', comment).strip()
        if comment in SocialConfig.comment_reply:
            return SocialConfig.comment_reply[comment]
        return None


class KuaishouRpaProcess:
    def __init__(self, search_keyword, reply_keyword, kuaishou_search_idx):
        self.reply_keyword = reply_keyword
        self.search_keyword = search_keyword
        self.kuaishou_search_idx = kuaishou_search_idx
        self.browser_tab = AgentConfig.browser_tab[Config.app_type_kuaishou]
        self.last_comment = None
        self.last_comment_pos_y = 0
        self.last_x = 0
        self.last_y = 0

    @classmethod
    def get_kuaishou_profile_url(cls):
        # AgentBrowser.change_browser_tab(AgentConfig.browser_tab[Config.app_type_tiktok][0])
        x, y = AgentConfig.kuaishou_avatar_pos
        auto_func(pyautogui.moveTo, x, y)
        time.sleep(1)
        # add_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][0] + 1)
        x, y = x, y + 75
        auto_func(pyautogui.click, x, y, clicks=1)
        time.sleep(3)
        url = AgentBrowser.get_browser_url()
        if url == 'https://www.kuaishou.com/' or not url.startswith('http'):
            return None
        close_current_tab()
        return url

    @classmethod
    def follow_each_other(cls, kuaishou_profile_url):
        if kuaishou_profile_url is None:
            return
        AgentBrowser.change_browser_tab(AgentConfig.browser_tab[Config.app_type_kuaishou][0])
        AgentBrowser.open_in_current_tab(url=kuaishou_profile_url)
        # add_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][0] + 1, override=True)
        # AgentBrowser.crack_tiktok_code(sleep_time=3)
        # AgentConfig.browser_tab[Config.app_type_tiktok].insert(1, 2)
        kuaishou_follow = Config.kuaishou_follow_eachother[0]
        kuaishou_unfollow = Config.kuaishou_unfollow[0]
        wait_until_either_show(kuaishou_follow, kuaishou_unfollow, region=AgentConfig.kuaishou_search_follow_region,
                               max_count=20)
        time.sleep(2)
        pos = pyautogui.locateCenterOnScreen(kuaishou_follow, region=AgentConfig.kuaishou_search_follow_region)
        if pos is not None:
            auto_func(pyautogui.click, pos.x, pos.y)
            time.sleep(1)
            logging.info('关注用户完成: ' + kuaishou_profile_url)
        else:
            logging.info('你已关注用户: ' + kuaishou_profile_url)
        set_app_followed(SocialConfig.kuaishou_profile_url, kuaishou_profile_url)
        # remove_browser_tab(Config.app_type_tiktok, AgentConfig.browser_tab[Config.app_type_tiktok][1])
        # close_current_tab()

    def search(self):
        if len(self.browser_tab) == 1:
            # AgentBrowser.change_browser_tab(str(self.browser_tab[0]))
            time.sleep(3)
            pyperclip.copy(self.search_keyword)
            time.sleep(0.2)
            auto_func(pyautogui.click, SocialConfig.kuaishou_search_x, SocialConfig.kuaishou_search_y)
            time.sleep(0.2)
            auto_func(pyautogui.hotkey, 'ctrl', 'a')
            time.sleep(0.2)
            auto_func(pyautogui.hotkey, 'backspace')
            time.sleep(0.2)
            auto_func(pyautogui.hotkey, 'ctrl', 'v')
            time.sleep(0.2)
            auto_func(pyautogui.hotkey, 'enter')
            time.sleep(3)
            # add_browser_tab(Config.app_type_kuaishou, self.browser_tab[0] + 1)
            self.browser_tab.append(self.browser_tab[0] + 1)
            self.kuaishou_search_idx['keyword_idx'] = self.kuaishou_search_idx['keyword_idx'] + 1

        if len(self.browser_tab) == 2:
            AgentBrowser.change_browser_tab(str(self.browser_tab[1]))
            kuaishou_video_tab = Config.kuaishou_video_tab[0]
            pos = util.wait_until_object_show(kuaishou_video_tab, (41, 571, 100, 100), 20, 0.9)
            # pos = autogui.locateCenterOnScreen(kuaishou_video_tab, region=AgentConfig.chrome_window_xy)
            if pos is not None:
                auto_func(pyautogui.click, SocialConfig.kuaishou_video_x, SocialConfig.kuaishou_video_y)
            time.sleep(3)
            if self.kuaishou_search_idx['video_idx'] == 0:
                self.view_video()
                self.kuaishou_search_idx['video_idx'] = self.kuaishou_search_idx['video_idx'] + 1
                # AgentBrowser.rpa_log(Config.app_type_kuaishou, '视频地址: ' + AgentBrowser.get_browser_url())
                url = AgentBrowser.get_browser_url()
                logging.info('视频地址: ' + url)
                if kuaishou_url_cache.get(url) is not None:
                    self.next_video()
                    return
                else:
                    kuaishou_url_cache.put(url, str(datetime.now().timestamp()))
                    if SocialConfig.kuaishou_id is not None:
                        cache_file_name = 'kuaishou' + '_' + Config.channel_name + '_' + SocialConfig.kuaishou_id + '.log'
                        AgentBrowser.append_url_cache(cache_file_name, url)
                time.sleep(3)
                self.follow_author()
                self.like_video()
                kuaishou_cache.clear()
            self.like_reply_batch()

    def view_video(self):
        x, y = AgentConfig.chrome_window_xy[0] + random.randint(717, 929), AgentConfig.chrome_window_xy[1] + 1011
        auto_func(pyautogui.moveTo, x, y)
        time.sleep(0.3)
        auto_func(pyautogui.click, x, y)
        time.sleep(0.3)
        auto_func(pyautogui.click, AgentConfig.chrome_window_xy[0] + 700, AgentConfig.chrome_window_xy[1] + 580)

    def like_reply_batch(self):
        auto_func(pyautogui.scroll, -1080)
        time.sleep(2)
        reply = Config.kuaishou_reply[0]
        bottom = Config.kuaishou_bottom[0]
        finish_region = (1563, 70, 220, 960)
        is_finished = autogui.locateOnScreen(bottom, region=finish_region, binarize_threshold=120, threshold=90)
        count = 0
        region = (AgentConfig.chrome_window_xy[0] + 1456, AgentConfig.chrome_window_xy[1], 444, AgentConfig.chrome_window_xy[3])
        while is_finished is None and count < 5:
            if SocialConfig.abort:
                return
            pos_list = autogui.locateAllOnScreen(reply, region=region)
            if len(pos_list) == 0 or AgentConfig.kuaishou_current_reply >= AgentConfig.kuaishou_max_reply:
                is_finished = True
            else:
                x, y = pyautogui.center(pos_list[0])
                if x == self.last_x and y == self.last_y:
                    auto_func(pyautogui.hotkey, 'f5')
                    time.sleep(3)
                    is_finished = True
                    logging.info('视频刷新: ' + AgentBrowser.get_browser_url())
                    break
                else:
                    self.last_x, self.last_y = x, y
                auto_func(pyautogui.moveTo, x + 70, y)
                if len(pos_list) >= 2:
                    phrase_x, phrase_y = x, y + 84
                    x, y = pyautogui.center(pos_list[1])
                    if self.like_reply(x, y, phrase_x, phrase_y) == -1:
                        is_finished = True
                        break
                else:
                    self.like_reply(x, y)
                auto_func(pyautogui.scroll, -540)
                is_finished = pyautogui.locateOnScreen(bottom, region=region)
                count = count + 1
        if is_finished is not None and count < 2:
            self.next_video()

    def next_video(self):
        auto_func(pyautogui.click, AgentConfig.chrome_window_xy[0] + 700, AgentConfig.chrome_window_xy[1] + 580)
        auto_func(pyautogui.hotkey, 'down')
        time.sleep(3)
        AgentConfig.kuaishou_current_reply = 0
        # AgentBrowser.rpa_log(Config.app_type_kuaishou, '视频地址: ' + AgentBrowser.get_browser_url())
        logging.info('视频地址: ' + AgentBrowser.get_browser_url())
        auto_func(pyautogui.click, AgentConfig.chrome_window_xy[0] + 700, AgentConfig.chrome_window_xy[1] + 580)
        self.kuaishou_search_idx['video_idx'] = self.kuaishou_search_idx['video_idx'] + 1
        self.follow_author()
        self.like_video()
        kuaishou_cache.clear()

    def like_reply(self, x, y, phrase_x=0, phrase_y=0):
        if phrase_x == 0:
            return 0
        auto_func(pyautogui.moveTo, phrase_x, phrase_y)
        time.sleep(1)
        screen = pyautogui.screenshot(region=(phrase_x - 250, phrase_y - 20, 500, 40))
        if self.contain_at_sign(screen):
            return
        if not autogui.click_if_not_link(phrase_x, phrase_y, clicks=3):
            logging.info('不是文字内容，跳过该评论')
            return
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.2)
        comment = pyperclip.paste()
        if comment is not None:
            comment = comment.strip()
        if comment == self.last_comment and y == self.last_comment_pos_y:
            return -1
        else:
            self.last_comment = comment
            self.last_comment_pos_y = y
        if kuaishou_cache.get(comment) is not None or len(comment) == 0:
            return 0
        else:
            kuaishou_cache.put(comment, '')
        reply = self.get_reply(comment)
        # AgentBrowser.rpa_log(Config.app_type_kuaishou, '评论: ' + comment)
        logging.info('评论: ' + comment)
        if reply is not None:
            auto_func(pyautogui.click, x - 75, y)
            time.sleep(1)
            reply = reply.strip()
            pyperclip.copy(reply)
            # AgentBrowser.rpa_log(Config.app_type_kuaishou, '回复: ' + reply)
            logging.info('回复: ' + reply)
            auto_func(pyautogui.click, x, y)
            time.sleep(1)
            auto_func(pyautogui.click, x, y + 60)
            time.sleep(1)
            auto_func(pyautogui.hotkey, 'ctrl', 'v')
            time.sleep(1)
            auto_func(pyautogui.hotkey, 'enter')
        AgentConfig.kuaishou_current_reply = AgentConfig.kuaishou_current_reply + 1
        return 1

    def get_reply(self, comment):
        for s in self.reply_keyword:
            if s in comment:
                answer = qa_call(comment, Config.channel_name, Config.channel_user)
                if len(answer) == 0:
                    return None
                return answer
        comment = re.sub(r'[\(\[].*?[\)\]]', '', comment).strip()
        if comment in SocialConfig.comment_reply:
            return SocialConfig.comment_reply[comment]
        return None

    def follow_author(self):
        if self.check_fans_status():
            pos = pyautogui.center(AgentConfig.kuaishou_author_follow_region)
            auto_func(pyautogui.click, pos.x, pos.y)
            time.sleep(0.5)
            # AgentBrowser.rpa_log(Config.app_type_kuaishou, '关注操作完成')
            logging.info('关注操作完成')

    def like_video(self):
        time.sleep(1)
        kuaishou_video_like = Config.kuaishou_video_like[0]
        kuaishou_wan = Config.kuaishou_wan[0]
        pos = autogui.locateCenterOnScreen(kuaishou_video_like, region=AgentConfig.kuaishou_video_like_region,
                                           binarize_threshold=120, threshold=0.9)
        kuaishou_wan_pos = autogui.locateCenterOnScreen(kuaishou_wan, region=AgentConfig.kuaishou_video_like_region,
                                                        binarize_threshold=120)
        if pos is not None and kuaishou_wan_pos is None and randrange(10) % 3 == 0:
            auto_func(pyautogui.click, pos.x, pos.y)
            # AgentBrowser.rpa_log(Config.app_type_kuaishou, '视频点赞操作完成')
            logging.info('视频点赞操作完成')

    def check_fans_status(self):
        kuaishou_follow = Config.kuaishou_follow[0]
        flag = pyautogui.locateOnScreen(kuaishou_follow, region=AgentConfig.kuaishou_author_follow_region)
        if flag is None:
            return False
        x, y = AgentConfig.kuaishou_user_icon
        auto_func(pyautogui.click, x, y)
        time.sleep(3)
        # add_browser_tab(Config.app_type_kuaishou, AgentConfig.browser_tab[Config.app_type_kuaishou][1] + 1)
        self.browser_tab.append(self.browser_tab[0] + 1)
        x, y = AgentConfig.kuaishou_author_fan_pos
        auto_func(pyautogui.click, x, y, clicks=2)
        time.sleep(0.5)
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.5)
        # remove_browser_tab(Config.app_type_kuaishou, AgentConfig.browser_tab[Config.app_type_kuaishou][2])
        self.browser_tab.pop()
        fan_number = pyperclip.paste()
        close_current_tab()
        if fan_number is not None:
            fan_number = fan_number.strip()
            # AgentBrowser.rpa_log(Config.app_type_kuaishou, '用户关注数: ' + fan_number)
            logging.info('用户关注数: ' + fan_number)
            if fan_number.isnumeric():
                if int(fan_number) < AgentConfig.kuaishou_author_fan_max:
                    return True
        return False

    def contain_at_sign(self, screen):
        base_data = np.asarray(screen)
        at_color = [254, 54, 102]
        for row in base_data:
            for col in row:
                if list(col) == at_color:
                    return True
        return False


class QqRpaProcess:
    def __init__(self, keyword, qq_search_idx):
        super(QqRpaProcess, self).__init__()
        self.keyword = keyword
        self.qq_search_idx = qq_search_idx

    def search(self):
        if self.qq_search_idx['keyword_idx'] < len(self.keyword):
            self.qq_search_add_service(self.keyword[self.qq_search_idx['keyword_idx']])

    def qq_contact_exists(self):
        qq_contact_exist = Config.qq_contact_exist[0]
        resolution = pyautogui.size()
        region = (resolution.width / 4, resolution.height / 4,
                  resolution.width / 2, resolution.height / 2)
        pos = pyautogui.locateOnScreen(qq_contact_exist, region=region)
        if pos is not None:
            return True
        return False

    def qq_search_add_people(self, search_str):
        pyperclip.copy(search_str)
        pyautogui.click(SocialConfig.qq_people_tab_x, SocialConfig.qq_people_tab_y)
        time.sleep(0.2)
        pyautogui.click(SocialConfig.qq_people_search_x, SocialConfig.qq_people_search_y)
        auto_func(pyautogui.hotkey, 'ctrl', 'a')
        auto_func(pyautogui.hotkey, 'backspace')
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.hotkey('enter')
        time.sleep(3)
        add_people_btn_image = Config.add_people_btn_image[0]
        pos = pyautogui.locateOnScreen(add_people_btn_image, region=SocialConfig.qq_contact_region)
        if pos is not None:
            if SocialConfig.abort:
                return
            x, y = pyautogui.center(pos)
            pyautogui.click(x, y)
            time.sleep(0.2)
            if self.qq_contact_exists():
                pyautogui.hotkey('alt', 'f4')
            else:
                pyautogui.hotkey('enter')
                time.sleep(0.2)
                pyautogui.hotkey('enter')

    def qq_search_add_service(self, search_str):
        if self.qq_search_idx['page'] == 0:
            x, y = AgentConfig.app_region[Config.app_type_qq][0], AgentConfig.app_region[Config.app_type_qq][1]
            pyautogui.click(x + 180, y + 20)
            time.sleep(0.5)
            pyautogui.click(x + 109, y + 64)
            time.sleep(2)

            pyperclip.copy(search_str)
            pyautogui.click(SocialConfig.qq_service_tab_x, SocialConfig.qq_service_tab_y)
            time.sleep(0.2)
            pyautogui.click(SocialConfig.qq_service_search_x, SocialConfig.qq_service_search_y)
            auto_func(pyautogui.hotkey, 'ctrl', 'a')
            auto_func(pyautogui.hotkey, 'backspace')

            pyautogui.hotkey('ctrl', 'v')
            pyautogui.hotkey('enter')
            time.sleep(3)
            auto_func(pyautogui.click, SocialConfig.show_online_checkbox_x, SocialConfig.show_online_checkbox_y)
            time.sleep(1)
            auto_func(pyautogui.click, SocialConfig.show_online_checkbox_x, SocialConfig.show_online_checkbox_y)
            time.sleep(2)

        self.qq_add_service()
        qq_search_next_image = Config.qq_search_next[0]
        qq_search_next_pos = pyautogui.locateCenterOnScreen(qq_search_next_image, region=SocialConfig.qq_contact_region)
        if qq_search_next_pos is not None:
            auto_func(pyautogui.click, qq_search_next_pos.x, qq_search_next_pos.y)
            time.sleep(3)
            self.qq_search_idx['page'] = self.qq_search_idx['page'] + 1
        else:
            self.qq_search_idx['keyword_idx'] = self.qq_search_idx['keyword_idx'] + 1

    def qq_add_service(self):
        add_service_btn_image = Config.add_service_btn_image[0]
        pos_list = list(pyautogui.locateAllOnScreen(add_service_btn_image, region=SocialConfig.qq_contact_region))

        while True:
            for pos in pos_list:
                if SocialConfig.abort:
                    return
                x, y = pyautogui.center(pos)
                self.get_contact_nick(x, y)
                pyautogui.click(x, y)
                time.sleep(0.2)
                if self.qq_contact_exists():
                    pyautogui.hotkey('alt', 'f4')
                else:
                    pyautogui.hotkey('enter')
                    time.sleep(2)
                    pyautogui.hotkey('enter')
                    # pyautogui.hotkey('alt', 'f4')
                time.sleep(1)
            qq_search_sample = pyautogui.screenshot(region=SocialConfig.qq_search_sample_region)
            pyautogui.scroll(-1080)
            s = pyautogui.locateOnScreen(qq_search_sample, region=SocialConfig.qq_search_sample_region)
            if s is not None:
                break
            pos_list = list(pyautogui.locateAllOnScreen(add_service_btn_image, region=SocialConfig.qq_contact_region))

    def get_contact_nick(self, x, y):
        auto_func(pyautogui.moveTo, x, y - 25)
        time.sleep(0.2)
        auto_func(pyautogui.drag, 0, -35, 0.2)
        time.sleep(0.2)
        auto_func(pyautogui.hotkey, 'ctrl', 'c')
        time.sleep(0.2)
        nick = pyperclip.paste().split('\r\n')[0].strip()
        if len(nick) == 0:
            return
        data = {
            "appId": Config.app_type_dict[Config.app_type_qq],
            "contactName": nick
        }
        add_app_contact(data)


class SocialRpa:
    @classmethod
    def stop_social_rpa(cls):
        SocialConfig.abort = True

    @classmethod
    def tiktok_search(cls, data):
        SocialConfig.abort = False
        search_keyword = data['searchStr']
        reply_keyword = data['replyStrList']
        TiktokRpaProcess(search_keyword, reply_keyword).start()

    @classmethod
    def show_contact_window(cls):
        x, y = AgentConfig.app_region[Config.app_type_qq][0], AgentConfig.app_region[Config.app_type_qq][1]
        pyautogui.click(x + 180, y + 20)
        time.sleep(0.5)
        pyautogui.click(x + 109, y + 64)
        time.sleep(2)

    @classmethod
    def start_qq_search(cls, data):
        cls.show_contact_window()
        SocialConfig.abort = False
        search_keyword = data['searchStrList'][0]
        QqRpaProcess(search_keyword).start()

    @classmethod
    def start_qq_upload(cls, data):
        cls.show_contact_window()
        SocialConfig.abort = False
        search_keyword = data['searchStrList']
        QqRpaProcess(search_keyword).start()

    @classmethod
    def social_rpa_status(cls):
        return SocialConfig.abort


class SocialProcess(Thread):
    app_status = []
    last_app_status = []

    def __init__(self, rpa_guide_data, current_app_type):
        super(SocialProcess, self).__init__()
        self.tiktok_search_idx = {'keyword_idx': -1, 'video_idx': 0}
        self.kuaishou_search_idx = {'keyword_idx': -1, 'video_idx': 0}
        self.qq_search_idx = {'keyword_idx': -1, 'page': 0}
        self.rpa_guide_data = None
        self.current_app_type = None
        self.rpa_guide_data = rpa_guide_data
        self.current_app_type = current_app_type
        self.last_guide_time = time.time()
        self.guide_work_time = time.time()
        self.guide_work_time = random.randint(36000, 43200)
        self.guide_sleep_time = random.randint(28800, 36000)

    def run(self):
        while not SocialConfig.abort:
            try:
                self.process()
            except Exception as e:
                logging.error("Exception occurred", exc_info=True)
                # raise e

    def process(self):
        work_time = time.time() - self.last_guide_time - self.guide_work_time
        if work_time < 0:
            self.rpa_guide()
            time.sleep(random.randint(AgentConfig.guide_wait_min_time, AgentConfig.guide_wait_max_time))
            # time.sleep(1)
        else:
            if work_time < self.guide_sleep_time:
                time.sleep(1)
            else:
                self.last_guide_time = time.time()
                self.guide_work_time = random.randint(36000, 43200)
                self.guide_sleep_time = random.randint(28800, 36000)

    def rpa_guide(self):
        if self.rpa_guide_data is None:
            return

        if self.current_app_type == Config.app_type_tiktok:
            if self.tiktok_search_idx['video_idx'] >= AgentConfig.guide_wait_max_count:
                self.abort = True
                return
            if SocialConfig.tiktok_id is None:
                SocialConfig.tiktok_id = TiktokRpaProcess.get_tiktok_id()
                load_url_cache(tiktok_url_cache, 'tiktok', SocialConfig.tiktok_id)
                logging.info('获取抖音用户ID: ' + SocialConfig.tiktok_id)
            TiktokRpaProcess.follow_each_other(get_unfollowed_info(10, SocialConfig.tiktok_id))
            # TiktokRpaProcess.follow_each_other('2115852133')
            TiktokRpaProcess(self.rpa_guide_data['searchStr'],
                             re.split(r'\W+', self.rpa_guide_data['replyKeyword']),
                             self.tiktok_search_idx).search()
        elif self.current_app_type == Config.app_type_kuaishou:
            if self.kuaishou_search_idx['video_idx'] >= AgentConfig.guide_wait_max_count:
                self.abort = True
                return
            if SocialConfig.kuaishou_id is None:
                SocialConfig.kuaishou_profile_url = KuaishouRpaProcess.get_kuaishou_profile_url()
                if 'profile' in SocialConfig.kuaishou_profile_url:
                    SocialConfig.kuaishou_id = SocialConfig.kuaishou_profile_url.split("profile/", 1)[1]
                load_url_cache(kuaishou_url_cache, 'kuaishou', SocialConfig.kuaishou_id)
                logging.info('获取快手用户首页URL: ' + SocialConfig.kuaishou_profile_url)
            KuaishouRpaProcess(self.rpa_guide_data['searchStr'],
                               re.split(r'\W+', self.rpa_guide_data['replyKeyword']),
                               self.kuaishou_search_idx).search()
            KuaishouRpaProcess.follow_each_other(get_unfollowed_info(11, SocialConfig.kuaishou_profile_url))
        elif self.current_app_type == Config.app_type_qq:
            QqRpaProcess(re.split(r'\W+', self.rpa_guide_data['searchStr']), self.qq_search_idx).search()
