# cython: language_level=3
import subprocess
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pyautogui
import pyperclip
from PIL import ImageFilter

from landingbj import util
from landingbj.agent_config import AgentConfig, remove_browser_tab
from landingbj.config import Config
from landingbj.util import copy_string, type_string


class AgentBrowser:
    @classmethod
    def account_auth(cls, data, app_id):
        username = data['username']
        password = data['password']
        user_x, user_y = AgentConfig.username_pos[app_id]
        copy_string(username, user_x, user_y)
        if app_id == Config.app_type_skype:
            pyautogui.hotkey('enter')
            time.sleep(0.5)
        password_x, password_y = AgentConfig.password_pos[app_id]
        type_string(password, password_x, password_y)
        time.sleep(0.5)
        pyautogui.hotkey('enter')
        if app_id == Config.app_type_skype:
            time.sleep(2)
            pyautogui.hotkey('enter')
        return AgentConfig.LOGIN_SUCCESS

    @classmethod
    def input_mobile_code(cls, data, app_id):
        valid_code = data['validCode']
        x, y = AgentConfig.valid_code_pos[app_id]
        type_string(valid_code, x, y)
        pyautogui.click(AgentConfig.account_btn_pos[app_id])
        return AgentConfig.LOGIN_SUCCESS

    @classmethod
    def send_mobile_code(cls, data, app_id):
        username = data['username']
        user_x, user_y = AgentConfig.username_pos[app_id]
        copy_string(username, user_x, user_y)
        time.sleep(0.2)
        pyautogui.click(AgentConfig.valid_code_btn_pos[app_id])
        AgentBrowser.crack_tiktok_code()
        return AgentConfig.NUMBER_CODE_MOBILE

    @classmethod
    def start_webpage(cls, url):
        tmp_dir = AgentConfig.chrome_tmp_dir + '/'
        window_size = AgentConfig.chrome_window_size
        window_position = AgentConfig.chrome_window_position

        cls.open_page_by_chrome(window_size, window_position, url, tmp_dir)

    @classmethod
    def open_page_by_chrome(cls, window_size, window_position, url, tmp_dir, exists=False):
        if exists is False:
            s = '"{chrome}" --user-data-dir="{tmp_dir}" --window-size={window_size} ' \
                '--window-position={window_position} --disable-notifications ' \
                '--disable-features=Translate --new-tab {url}'
            command = s.format(chrome=AgentConfig.chrome_path, tmp_dir=tmp_dir, window_size=window_size,
                               window_position=window_position, url=url)
            subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        else:
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('backspace')
            pyperclip.copy(url)
            x, y = AgentConfig.chrome_title_bar_xy
            pyautogui.click(x, y)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.hotkey('enter')

    @classmethod
    def change_browser_tab(cls, tab_id):
        x, y = AgentConfig.chrome_title_bar_xy
        pyautogui.click(x, y)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', str(tab_id))
        time.sleep(0.1)

    @classmethod
    def remove_browser_tab(cls):
        browser_tab = AgentConfig.browser_tab
        remove_tab = {}
        for app in browser_tab:
            if app == Config.app_type_tiktok and len(browser_tab[app]) > 1:
                remove_tab[app] = browser_tab[app][1:]
            if app == Config.app_type_kuaishou and len(browser_tab[app]) > 1:
                remove_tab[app] = browser_tab[app][1:]

        removed_list = cls.sort_removed_tab(remove_tab)
        for app, tab in removed_list:
            cls.change_browser_tab(str(tab))
            pyautogui.hotkey('ctrl', 'w')
            remove_browser_tab(app, tab)

    @classmethod
    def sort_removed_tab(cls, remove_tab):
        result = []
        while cls.get_removed_tab_size(remove_tab) > 0:
            app_id, max_tab = cls.get_max_removed_tab(remove_tab)
            result.append((app_id, max_tab))
            remove_tab[app_id].remove(max_tab)
        return result

    @classmethod
    def get_removed_tab_size(cls, remove_tab):
        size = 0
        for app in remove_tab:
            size = size + len(remove_tab[app])
        return size

    @classmethod
    def get_max_removed_tab(cls, remove_tab):
        app_id = -1
        max_tab = -1
        for app in remove_tab:
            for tab in remove_tab[app]:
                if tab > max_tab:
                    max_tab, app_id = tab, app
        return app_id, max_tab

    @classmethod
    def crack_tiktok_code(cls, sleep_time=0):
        time.sleep(sleep_time)
        slide_search_region = AgentConfig.slide_search_region_tiktok
        if not util.wait_until_object_show(Config.slide_image_tiktok, slide_search_region, 6):
            return
        region = AgentConfig.slide_region_tiktok
        btn_x, btn_y = AgentConfig.slide_btn_x_tiktok, AgentConfig.slide_btn_y_tiktok
        refresh_x, refresh_y = AgentConfig.slide_refresh_x_tiktok, AgentConfig.slide_refresh_y_tiktok
        duration, offset = 1, AgentConfig.tiktok_slide_drag_offset
        gray_image = pyautogui.screenshot(region=region).convert('L')
        drag_distance = cls.get_tiktok_slide_distance(gray_image)

        while drag_distance < 0:
            pyautogui.click(refresh_x, refresh_y)
            time.sleep(2)
            gray_image = pyautogui.screenshot(region=region).convert('L')
            drag_distance = cls.get_tiktok_slide_distance(gray_image)

        time.sleep(0.5)
        pyautogui.moveTo(btn_x, btn_y)
        pyautogui.dragTo(btn_x + int(drag_distance) + offset, btn_y, duration, button='left')
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(sleep_time)

    @classmethod
    def get_tiktok_slide_distance(cls, gray_image):
        edge_data = np.asarray(gray_image.filter(ImageFilter.FIND_EDGES))
        x_list = []
        count = np.count_nonzero(edge_data > 200, axis=0)
        for i, value in enumerate(count):
            if 2 < i < 330 and 20 < value < 70:
                x_list.append(i)
        if len(x_list) == 4:
            return x_list[2] - x_list[0]
        return -1

    @classmethod
    def change_tiktok_theme(cls):
        tiktok_dark_theme = Config.tiktok_dark_theme
        region = AgentConfig.tiktok_slide_theme_region
        result = pyautogui.locateCenterOnScreen(tiktok_dark_theme, region=region)
        if result is not None:
            pyautogui.click(result.x, result.y)

    @classmethod
    def rpa_log(cls, app_id, content):
        if AgentConfig.log_level == 0:
            return
        guide_tmp_file = AgentConfig.guide_tmp_file_dict[app_id]
        file = open(guide_tmp_file, 'a', encoding='utf-8')
        line = '[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] ' + content + '\n'
        file.write(line)
        file.close()

    @classmethod
    def append_url_cache(cls, cache_file_name, url):
        if not url.startswith('http'):
            return
        cache_file_path = Path(AgentConfig.guide_url_tmp_dir + '/' + cache_file_name)
        file = open(cache_file_path, 'a', encoding='utf-8')
        line = str(datetime.now().timestamp()) + ',' + url + '\n'
        file.write(line)
        file.close()

    @classmethod
    def get_browser_url(cls):
        x, y = AgentConfig.chrome_title_bar_xy
        pyautogui.click(x, y)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)
        return pyperclip.paste()

    @classmethod
    def open_in_current_tab(cls, url):
        pyperclip.copy(url)
        x, y = AgentConfig.chrome_title_bar_xy
        pyautogui.click(x, y)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('backspace')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.hotkey('enter')
