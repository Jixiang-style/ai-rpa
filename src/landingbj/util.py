#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# util.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#

# cython: language_level=3
import hashlib
import os
import subprocess
import socket
import time
from collections import OrderedDict
from sys import platform
from io import BytesIO
from typing import Optional

import pyautogui
import pyperclip
from PIL import ImageTk, Image

from landingbj import autogui
from landingbj.config import Config
from landingbj.qa import get_image_by_url

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> Optional[str]:
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: str) -> None:
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()


def send_to_clipboard(image):
    if platform == "win32":
        import win32clipboard
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
    elif platform == 'linux':
        image_name = image.filename.split('/')[-1].split('.')[0]
        image_path = Config.image_tmp_dir + image_name + '.png'
        image.save(image_path, format='png')
        subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', image_path])
        os.remove(image_path)


def mouse_left_is_pressed():
    if platform == "win32":
        import win32api
        from win32con import VK_LBUTTON, SM_SWAPBUTTON, VK_RBUTTON
        left_pos = VK_LBUTTON
        if win32api.GetSystemMetrics(SM_SWAPBUTTON) > 0:
            left_pos = VK_RBUTTON
        left_state = win32api.GetAsyncKeyState(left_pos)
        if left_state < 0:
            return True
    return False


def mouse_right_is_pressed():
    if platform == "win32":
        import win32api
        from win32con import VK_LBUTTON, SM_SWAPBUTTON, VK_RBUTTON
        right_pos = VK_RBUTTON
        if win32api.GetSystemMetrics(SM_SWAPBUTTON) > 0:
            right_pos = VK_LBUTTON
        left_state = win32api.GetAsyncKeyState(right_pos)
        if left_state < 0:
            return True
    return False


def mouse_is_moving():
    if platform == "win32":
        import win32api
        saved_pos = win32api.GetCursorPos()
        time.sleep(0.2)
        cur_pos = win32api.GetCursorPos()
        if saved_pos != cur_pos:
            return True
    return False

# 判断鼠标是否有动作，其实就是判断人是否介入在操作机器
def mouse_is_working():
    return mouse_left_is_pressed() or mouse_right_is_pressed() or mouse_is_moving()


def get_tk_icon(image_path, size):
    icon = Image.open(image_path).resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(icon)


image_cache = {}


def get_image(app_icon_url, size=(25, 25)):
    if app_icon_url not in image_cache:
        app_icon = ImageTk.PhotoImage(get_image_by_url(app_icon_url).resize(size, Image.ANTIALIAS))
        image_cache[app_icon_url] = app_icon

    return image_cache[app_icon_url]


def get_current_settings():
    settings = {
        'channel_name': Config.channel_name,
        'channel_user': Config.channel_user,
        'rpa_robot_flag': Config.rpa_robot_flag,
        'rpa_timer_flag': Config.rpa_timer_flag,
        'rpa_monitor_flag': Config.rpa_monitor_flag,
        'login_status': Config.login_status
    }
    return settings


def check_login_status(channel_name, channel_user, login_status):
    if login_status == encode_login_status(channel_name, channel_user):
        return True
    return False


def encode_login_status(channel_name, channel_user):
    host_name = socket.gethostname()
    source = channel_name + channel_user + host_name
    md5 = hashlib.md5(source.encode()).hexdigest()
    return md5


def wait_until_object_show(image, region, max_count, period=0.5, threshold=0.8):
    count = 0
    while count < max_count:
        result = autogui.locateOnScreen(image, region=region, threshold=threshold)
        if result is not None:
            return True
        else:
            time.sleep(period)
            count = count + 1
    return False


def copy_string(string, x, y):
    pyperclip.copy(string)
    time.sleep(1)
    pyautogui.click(x, y)
    pyautogui.click(x, y, 2, interval=0.1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)


def type_string(string, x, y):
    pyperclip.copy(string)
    time.sleep(1)
    pyautogui.click(x, y)
    pyautogui.click(x, y, 2, interval=0.1)
    str_list = list(string)
    for s in str_list:
        pyautogui.press(s)
    time.sleep(1)


def wait_until_either_show(image1, image2, region, max_count, period=0.5):
    count = 0
    while count < max_count:
        result1 = pyautogui.locateOnScreen(image1, region=region)
        result2 = pyautogui.locateOnScreen(image2, region=region)
        if result1 is not None or result2 is not None:
            return True
        else:
            time.sleep(period)
            count = count + 1
    return False
