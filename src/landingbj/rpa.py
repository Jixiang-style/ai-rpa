#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# rpa.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#


# cython: language_level=3
import logging
import re
from sys import platform
from threading import Thread, Lock

import numpy as np
import pyautogui
import pyperclip
import time
import pyscreeze

from ai.config import AiConfig

from landingbj import util, autogui
from ai import screen_util
from landingbj.config import Config
from ai.image import find_logo, fast_logo, image_binarize, get_search_position, find_message_no_logo, print_image
from ai.new_message import find_new_message, generate_red_dot, red_dot_vertical_valid, red_dot_horizontal_valid
from landingbj.qa import qa_call, get_rpa_task, get_repeater_task, get_repeater_contact, add_repeater_message, \
    get_rpa_task_image
from landingbj.util import send_to_clipboard, mouse_left_is_pressed

_DEBUG_ = AiConfig.debug_flag

lock = Lock()
pos_stack_lock = Lock()

# 同步锁
def synchronized(func):
    def synced_func(*args, **kws):
        with lock:
            return func(*args, **kws)

    return synced_func


def synchronized_pos_stack(func):
    def synced_func(*args, **kws):
        with pos_stack_lock:
            return func(*args, **kws)

    return synced_func


class PositionStack:
    def __init__(self):
        self.pos_stack = []

    @synchronized_pos_stack
    def pop(self):
        if len(self.pos_stack) == 0:
            return None
        return self.pos_stack.pop()

    @synchronized_pos_stack
    def push(self, pos):
        if len(self.pos_stack) == 0:
            self.pos_stack.append(pos)
        else:
            self.pos_stack.append(self.pos_stack[-1])


pos_stack = PositionStack()

# 归位
def reset_position(func):
    def wrapper(*args, **kws):
        pos1 = pyautogui.position()
        pos_stack.push(pos1)
        result = func(*args, **kws)
        pos2 = pos_stack.pop()
        pyautogui.moveTo(pos2)
        return result

    return wrapper


class RpaProcess(Thread):
    app_status = []
    last_app_status = []

    def __init__(self, conf, gui, app_idx):
        super(RpaProcess, self).__init__()
        self.conf = conf
        self.abort = False
        self.last_question = None
        self.last_repeater_message = None
        self.last_qa_time = None
        self.last_timer_time = None
        self.last_repeater_time = None
        self.last_search_contact_time = None
        self.red_dot_array = None
        self.red_index = None
        self.red_count = None
        self.contacts = None
        self.find_logo_flag = None
        self.find_logo_count = None
        self.black_list = None
        self.current_contact = None
        self.gui = gui
        self.last_active_count = 0
        self.active_count = 0
        self.crop_regions = None
        self.dial_check_lines = None
        self.repeater_check_lines = None
        self.timer_disable_set = set()
        self.window_change_state = None
        self.app_idx = app_idx

    def run(self):
        self.last_active_count = len(self.conf.input_region)
        self.active_count = len(self.conf.input_region)
        self.last_question = [''] * len(self.conf.input_region)
        self.last_repeater_message = [{}] * len(self.conf.input_region)
        self.last_qa_time = [0] * len(self.conf.input_region)
        self.last_timer_time = [0] * len(self.conf.input_region)
        self.last_repeater_time = [0] * len(self.conf.input_region)
        self.last_search_contact_time = [0] * len(self.conf.input_region)
        self.contacts = [0] * len(self.conf.input_region)
        self.black_list = [set()] * len(self.conf.input_region)
        self.current_contact = ['$initial_contact$'] * len(self.conf.input_region)
        self.red_dot_array, self.red_index, self.red_count = generate_red_dot(Config.red_round_size)
        self.find_logo_flag = [0] * len(self.conf.input_region)
        self.find_logo_count = [0] * len(self.conf.input_region)
        self.dial_check_lines = [[]] * len(self.conf.input_region)
        self.repeater_check_lines = [[]] * len(self.conf.input_region)
        self.window_change_state = [False] * len(self.conf.input_region)

        self.crop_regions = [()] * len(self.conf.input_region)
        for i in range(len(self.crop_regions)):
            current_app_type = self.conf.app_type[i]
            self.crop_regions[i] = self.calc_region_moved(current_app_type)

        if Config.rpa_monitor_flag == 1:
            for i in range(len(self.conf.input_region)):
                current_app_type = self.conf.app_type[i]
                self.contacts[i] = get_repeater_contact(self.conf.channel_name, Config.app_type_dict[current_app_type],
                                                        self.conf.channel_user)
        time.sleep(0.5)
        while not self.abort:
            while util.mouse_is_working():
                time.sleep(0.5)
            try:
                self.process()
            except Exception as e:
                # pass
                # raise e
                logging.exception("message")

    @synchronized
    def move_app(self):
        self.gui.move_app()

    def process(self):
        i = 0
        while i < len(self.conf.input_region):
            if Config.rpa_timer_flag == 0 and Config.rpa_monitor_flag == 0 and Config.rpa_robot_flag == 0:
                i += 1
                time.sleep(0.1)
                continue

            if self.sync_topmost(i):
                RpaProcess.app_status[self.app_idx] = 1
            else:
                if self.app_idx == Config.attach_app_index and self.is_moved(i):
                    RpaProcess.app_status[self.app_idx] = 1
                    self.move_app()
                else:
                    RpaProcess.app_status[self.app_idx] = 0

            if RpaProcess.app_status[self.app_idx] != RpaProcess.last_app_status[self.app_idx]:
                self.move_app()
                RpaProcess.last_app_status[self.app_idx] = RpaProcess.app_status[self.app_idx]

            if RpaProcess.app_status[self.app_idx] == 0:
                i += 1
                time.sleep(0.256)
                continue

            try:
                if Config.rpa_timer_flag == 1:
                    if i not in self.timer_disable_set:
                        if time.time() - self.last_timer_time[i] > Config.timer_wait_time or self.last_timer_time[i] == 0:
                            self.rpa_timer(i, Config.rpa_task_timer)
                    else:
                        time.sleep(0.02)
                if Config.rpa_monitor_flag == 1:
                    if i not in self.timer_disable_set:
                        if time.time() - self.last_repeater_time[i] > Config.timer_wait_time or self.last_repeater_time[i] == 0:
                            self.rpa_timer(i, Config.rpa_task_monitor)
                        self.add_rpa_message(i)
                    else:
                        time.sleep(0.02)
                if Config.rpa_robot_flag == 1:
                    self.change_diag_window(i)
                    self.auto(i)

            except RuntimeError as e:
                if self.abort:
                    break
                self.find_logo_count[i] = 0
                self.find_logo_flag[i] = 0
                i -= 1
            i += 1

        if not self.abort:
            self.active_count = sum(RpaProcess.app_status)
            if self.active_count == 0:
                self.gui.rpa_stop()
                self.gui.master.wm_state('iconic')
            elif self.active_count != self.last_active_count:
                self.move_app()
                self.last_active_count = self.active_count

    def calc_region_moved(self, app_type):
        region = Config.app_min_region[app_type]
        screen_width, screen_height = pyautogui.size()
        search_offset_x, search_offset_y = Config.search_point_offset[app_type]
        input_icon_offset_x, input_icon_offset_y = Config.input_icon_offset
        send_button_offset_x, send_button_offset_y = Config.send_button_offset[app_type]

        min_width, min_height = region[0]
        input_up, input_down, input_left, input_right = region[1]

        if min_width >= screen_width or min_height >= screen_height:
            min_width = screen_width - Config.sample_icon_size
            min_height = screen_height - Config.sample_icon_size
            input_left, input_up, input_right, input_down = 0, 0, screen_width, screen_height

        offset_x, offset_y = screen_width - min_width, screen_height - min_height

        search_region_xl = search_offset_x
        search_region_yl = search_offset_y
        search_region_xr = search_offset_x + offset_x
        search_region_yr = search_offset_y + offset_y
        search_region = (search_region_xl, search_region_yl, search_region_xr, search_region_yr)

        input_region_xl = input_left
        input_region_yl = input_up
        input_region_xr = screen_width - input_right + input_icon_offset_x + Config.sample_icon_size
        input_region_yr = screen_height - input_down + input_icon_offset_y + Config.sample_icon_size
        input_region = (input_region_xl, input_region_yl, input_region_xr, input_region_yr)

        send_region_xl = min_width - send_button_offset_x
        send_region_yl = min_height - send_button_offset_y
        send_region_xr = screen_width - send_button_offset_x + Config.sample_icon_size
        send_region_yr = screen_height - send_button_offset_y + Config.sample_icon_size
        send_region = (send_region_xl, send_region_yl, send_region_xr, send_region_yr)

        return search_region, input_region, send_region

    @synchronized
    def is_moved(self, i):
        search_result, icon_result, send_btn_result, screenshot = self.sample_icon_exists_full(i)
        if search_result is not None and icon_result is not None and send_btn_result is not None:
            self.update_region(i, search_result, icon_result, send_btn_result, screenshot)
            self.gui.init_topmost_matrix()
            return True
        else:
            return False

    def update_region(self, i, search_region, icon_region, send_btn_region, screenshot):
        current_app_type = self.conf.app_type[i]
        old_app_region = self.conf.app_region[i]
        old_input_region = self.conf.input_region[i]
        old_search_sample_region = self.conf.search_pos[i]
        old_icon_pos_region = self.conf.icon_pos[i]
        old_send_btn_region = self.conf.send_btn_pos[i]

        dx1 = send_btn_region[0] - search_region[0] - (old_send_btn_region[0] - old_search_sample_region[0])
        dy1 = send_btn_region[1] - search_region[1] - (old_send_btn_region[1] - old_search_sample_region[1])
        new_app_width, new_app_height = old_app_region[2] + dx1, old_app_region[3] + dy1
        dx2, dy2 = old_search_sample_region[0] - old_app_region[0], old_search_sample_region[1] - old_app_region[1]
        new_app_x, new_app_y = search_region[0] - dx2,  search_region[1] - dy2
        self.conf.app_region[i] = (new_app_x, new_app_y, new_app_width, new_app_height)

        self.gui.config.app_region[self.app_idx] = (new_app_x, new_app_y, new_app_width, new_app_height)

        dx3 = send_btn_region[0] - icon_region[0] - (old_send_btn_region[0] - old_icon_pos_region[0])
        dy3 = send_btn_region[1] - icon_region[1] - (old_send_btn_region[1] - old_icon_pos_region[1])
        new_input_width, new_input_height = old_input_region[2] + dx3, old_input_region[3] + dy3
        dx4, dy4 = old_icon_pos_region[0] - old_input_region[0], old_icon_pos_region[1] - old_input_region[1]
        new_input_x, new_input_y = icon_region[0] - dx4,  icon_region[1] - dy4
        self.conf.input_region[i] = (new_input_x, new_input_y, new_input_width, new_input_height)

        self.conf.search_pos[i] = search_region
        self.conf.icon_pos[i] = icon_region
        self.conf.send_btn_pos[i] = send_btn_region

        if current_app_type in (Config.app_type_qq, Config.app_type_qq_full):
            self.conf.search_sample[i], self.conf.bin_search_sample[i] = self.get_dymatic_sample(search_region, screenshot)
            self.conf.send_btn_sample[i], self.conf.bin_send_btn_sample[i] = self.get_dymatic_sample(send_btn_region, screenshot)
        else:
            self.conf.search_sample[i], self.conf.bin_search_sample[i] = self.get_new_sample(search_region, screenshot)
            self.conf.send_btn_sample[i], self.conf.bin_send_btn_sample[i] = self.get_new_sample(send_btn_region, screenshot)
        self.conf.icon_sample[i], self.conf.bin_icon_sample[i] = self.get_new_sample(icon_region, screenshot)

    def get_new_sample(self, region, screenshot):
        right_down_x, right_down_y = region[0] + Config.sample_icon_size, region[1] + Config.sample_icon_size
        sample_image = screenshot.crop((region[0], region[1], right_down_x, right_down_y))
        bin_sample_image = image_binarize(sample_image, Config.image_binarize_threshold)
        return sample_image, bin_sample_image

    def get_dymatic_sample(self, region, screenshot):
        right_down_x, right_down_y = region[0] + Config.sample_icon_size, region[1] + Config.sample_icon_size
        sample_image = screenshot.crop((region[0], region[1], right_down_x, right_down_y))
        bin_sample_image = image_binarize(sample_image, Config.dymatic_binarize_threshold)
        return sample_image, bin_sample_image

    @synchronized
    @reset_position
    def sync_topmost(self, i):
        return self.topmost(i)

    def topmost_check(self, i):
        if Config.topmost_matrix[i][i] == -1 and Config.topmost_matrix[i][i] == 1:
            return True
        Config.topmost_matrix[i][i] = 1
        for j in range(len(Config.topmost_matrix[i])):
            if j == i:
                continue
            if Config.topmost_matrix[i][j] == 1:
                Config.topmost_matrix[j][j] = 0
        return self.topmost(i)

    # 置为最上层
    def topmost(self, i):
        current_app_type = self.conf.app_type[i]
        # 搜索框定位     # 小图标定位   # 发送按钮定位
        search_result, icon_result, send_btn_result = self.sample_icon_exists(i)
        if search_result is not None and icon_result is not None and send_btn_result is not None:
            return True

        if search_result is True or icon_result is True or send_btn_result is True:
            return False

        click_pos = None

        if search_result is not None:
            search_sample_region = self.conf.search_pos[i]
            if current_app_type == Config.app_type_ding6:
                click_pos = search_sample_region[0] + 50, search_sample_region[1]
            elif current_app_type == Config.app_type_whatsapp:
                click_pos = search_sample_region[0] - 50, search_sample_region[1]
            else:
                click_pos = search_sample_region[0], search_sample_region[1]

        if icon_result is not None:
            icon_pos_region = self.conf.input_region[i]
            click_pos = icon_pos_region[0] + 8, icon_pos_region[1] + 20

        if send_btn_result is not None:
            send_btn_region = self.conf.send_btn_pos[i]
            click_pos = send_btn_region[0], send_btn_region[1] - 50

        if click_pos is not None:
            pyautogui.click(click_pos[0], click_pos[1])
            time.sleep(0.5)
            search_result, icon_result, send_btn_result = self.sample_icon_exists(i)
            if search_result is not None and icon_result is not None and send_btn_result is not None:
                return True
        return False

    def test_moved(self, i, func, *args, **kwargs):
        if self.abort or mouse_left_is_pressed() is True:
            raise RuntimeError()

        current_app_type = self.conf.app_type[i]
        screenshot = autogui.screenshot()
        icon_pos_region = self.conf.send_btn_pos[i]

        if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
            icon_sample_image = image_binarize(self.conf.send_btn_sample[i], Config.image_binarize_threshold)
            bin_part = self.binarize_part(screenshot.convert('L'), self.region_to_diagonal(icon_pos_region))
            pos_result = pyautogui.locate(icon_sample_image, bin_part)
        elif current_app_type == Config.app_type_ding6 or current_app_type == Config.app_type_51job:
            pos_result = pyautogui.locate(self.conf.search_sample[i], screenshot, region=self.conf.search_pos[i])
        else:
            pos_result = pyautogui.locate(self.conf.send_btn_sample[i], screenshot, region=icon_pos_region)

        if pos_result is not None:
            func(*args, **kwargs)
        else:
            raise RuntimeError()

    def region_to_diagonal(self, region):
        xl, yl = region[0], region[1]
        xr, yr = region[0] + region[2], region[1] + region[3]
        return xl, yl, xr, yr

    def binarize_part(self, image, region, current_app_type=0):
        image_part = image.crop(region)
        if current_app_type in (Config.app_type_qq, Config.app_type_qq_full):
            bin_part = image_binarize(image_part.convert('L'), Config.dymatic_binarize_threshold)
        else:
            bin_part = image_binarize(image_part.convert('L'), Config.image_binarize_threshold)
        return bin_part

    # 三点定位
    def sample_icon_exists(self, i):
        search_sample_region = self.conf.search_pos[i]
        screenshot = autogui.screenshot()

        search_sample_image = self.conf.search_sample[i]
        bin_part = screenshot.crop(self.region_to_diagonal(search_sample_region))
        # 调试信息 {
        if _DEBUG_:
            print_image(search_sample_image, "sample_search.png")
            print_image(bin_part, "sample_icon_exists_1.png")
        # }
        pos_result1 = self.sample_icon_locate(search_sample_image, bin_part, search_sample_region)
        if pos_result1 is None and self.conf.app_type[i] == Config.app_type_qq:
            pos_result1 = screen_util.locate_one(search_sample_image, bin_part)

        icon_pos_region = self.conf.icon_pos[i]
        icon_sample_image = self.conf.bin_icon_sample[i]
        bin_part = self.binarize_part(screenshot, self.region_to_diagonal(icon_pos_region))
        # 调试信息 {
        if _DEBUG_:
            print_image(icon_sample_image, "sample_icon.png")
            print_image(bin_part, "sample_icon_exists_2.png")
        # }
        pos_result2 = self.sample_icon_locate(icon_sample_image, bin_part, icon_pos_region)

        send_btn_region = self.conf.send_btn_pos[i]
        send_btn_sample_image = self.conf.bin_send_btn_sample[i]
        bin_part = self.binarize_part(screenshot, self.region_to_diagonal(send_btn_region), self.conf.app_type[i])
        # 调试信息 {
        if _DEBUG_:
            print_image(send_btn_sample_image, "sample_botton.png")
            print_image(bin_part, "sample_icon_exists_3.png")
        # }
        pos_result3 = self.sample_icon_locate(send_btn_sample_image, bin_part, send_btn_region)

        return pos_result1, pos_result2, pos_result3

    def to_full_screen_location(self, pos_result, off_x, off_y):
        if pos_result is None:
            return None
        x, y = pos_result[0] + off_x, pos_result[1] + off_y
        width, height = pos_result[2], pos_result[3]
        return int(x), int(y), width, height

    def sample_icon_exists_full(self, i):
        screenshot = autogui.screenshot()

        binarized_search_region = self.binarize_part(screenshot, self.crop_regions[i][0], self.conf.app_type[i])
        search_sample_image = self.conf.bin_search_sample[i]
        pos_result1 = pyautogui.locate(search_sample_image, binarized_search_region)
        pos_result1 = self.to_full_screen_location(pos_result1, self.crop_regions[i][0][0], self.crop_regions[i][0][1])

        if pos_result1 is None:
            return None, None, None, screenshot
        binarized_send_btn_region = self.binarize_part(screenshot, self.crop_regions[i][2], self.conf.app_type[i])
        send_btn_sample_image = self.conf.bin_send_btn_sample[i]
        pos_result2 = pyautogui.locate(send_btn_sample_image, binarized_send_btn_region)
        pos_result2 = self.to_full_screen_location(pos_result2, self.crop_regions[i][2][0], self.crop_regions[i][2][1])

        if pos_result2 is None:
            return pos_result1, None, None, screenshot
        binarized_icon_region = self.binarize_part(screenshot, self.crop_regions[i][1])
        icon_sample_image = self.conf.bin_icon_sample[i]
        pos_result3 = pyautogui.locate(icon_sample_image, binarized_icon_region)
        pos_result3 = self.to_full_screen_location(pos_result3, self.crop_regions[i][1][0], self.crop_regions[i][1][1])

        return pos_result1, pos_result3, pos_result2, screenshot

    def sample_icon_locate(self, sample_image, screen_part, region):
        if self.gui.master.state() == 'normal':
            width, height, x, y = list(map(int, re.split('x|\\+', self.gui.master.geometry())))
            width, height, x, y = width + 40, height + 40, x - 20, y - 20
            left_x, left_y, right_x, right_y = region[0], region[1], region[0] + region[2], region[1] + region[3]
            dx = min(right_x, x + width) - max(left_x, x)
            dy = min(right_y, y + height) - max(left_y, y)
            if (dx >= 0) and (dy >= 0):
                return True
        return pyautogui.locate(sample_image, screen_part)

    @reset_position
    def add_rpa_message(self, i):
        current_app_type = self.conf.app_type[i]
        contact_names = self.contacts[i]
        if contact_names is None or len(contact_names) == 0:
            return

        for contact in contact_names:
            contact_name = contact['contactName']
            if contact_name in self.black_list[i] or \
                    (not self.valid_red_dot_exists(i) and not self.repeater_message_exists(i)):
                continue
            if self.current_contact[i] != contact_name or \
                    time.time() - self.last_search_contact_time[i] > Config.contact_wait_time:
                self.search_contact(contact_name, current_app_type, i)
                self.last_search_contact_time[i] = time.time()
            self.auto(i, contact)

    def repeater_message_exists(self, i):
        dialogue_region = self.conf.dialogue_region[i]
        current_app_type = self.conf.app_type[i]

        screenshot = autogui.screenshot().convert('L')
        if self.repeater_lines_is_changed(i, screenshot):
            logo_x, logo_y, my_message_exists = self.find_message(screenshot, dialogue_region, current_app_type)
        else:
            logo_x, logo_y = -1, -1
            time.sleep(0.128)

        if logo_x == -1:
            return False

        input_center_x = self.conf.send_btn_pos[i][0]
        input_center_y = self.conf.send_btn_pos[i][1] - Config.input_click_offset
        input_center_x, input_center_y = autogui.get_abs_region((input_center_x, input_center_y))
        pyautogui.click(input_center_x, input_center_y)
        self.update_repeater_check_lines(i, 4, screenshot, dialogue_region)

        if current_app_type == Config.app_type_whatsapp:
            dial_x, dial_y = int(logo_x + 20 * Config.scale_ratio), int(logo_y + Config.logo_offset_y - 20 * Config.scale_ratio)
        elif current_app_type == Config.app_type_line:
            dial_x, dial_y = int(logo_x + 20 * Config.scale_ratio), int(logo_y + Config.logo_offset_y - 20 * Config.scale_ratio)
        else:
            dial_x, dial_y = logo_x + Config.logo_offset_x, logo_y + Config.logo_offset_y

        if not self.abort:
            cursor_type = self.get_mouse_cursor_type(i, dial_x, dial_y)
            if cursor_type == Config.mouse_cursor_text or cursor_type == Config.mouse_cursor_normal:
                question = self.copy_question(dial_x, dial_y, dialogue_region, i)
                if question != '':
                    return True
        return False

    @synchronized
    def search_contact(self, contact_name, current_app_type, app_index):
        if not self.topmost_check(app_index):
            return False

        input_center_x = self.conf.send_btn_pos[app_index][0]
        input_center_y = self.conf.send_btn_pos[app_index][1] - 50
        input_center_x, input_center_y = autogui.get_abs_region((input_center_x, input_center_y))
        self.test_moved(app_index, pyautogui.click, input_center_x, input_center_y)

        search_x_offset, search_y_offset, search_target_offset = Config.rpa_timer_offset[current_app_type]
        if current_app_type == Config.app_type_ding6:
            app_region = self.conf.app_region[app_index]
            search_input_x, search_input_y = app_region[0] + app_region[2] / 2, app_region[1] + search_y_offset
            contact_region = (app_region[0], app_region[1],
                              app_region[0] + app_region[2] / 2, app_region[1] + app_region[2] / 3)
        elif current_app_type == Config.app_type_weibo:
            contact_region = self.conf.contact_region[app_index]
            crop_region = (contact_region[0], contact_region[1],
                           contact_region[0] + contact_region[2], contact_region[1] + contact_region[3] // 3)
            base_data = np.asarray(autogui.screenshot().convert('L').crop(crop_region), dtype=int)
            i = base_data.shape[1] * 2 // 3
            line = base_data[:, i]
            j = get_search_position(line, Config.weibo_search_height)
            if j == -1:
                j = search_y_offset
            search_input_x, search_input_y = contact_region[0] + i, contact_region[1] + j
        else:
            contact_region = self.conf.contact_region[app_index]
            search_input_x, search_input_y = contact_region[0] + search_x_offset, contact_region[1] + search_y_offset

        search_input_x, search_input_y = autogui.get_abs_region((search_input_x, search_input_y))

        if current_app_type in (Config.app_type_ding, Config.app_type_ding_gray, Config.app_type_ding_full):
            offset_x = self.conf.app_region[app_index][0] + Config.ding5_message_button_offset_x
            offset_y = self.conf.app_region[app_index][1] + Config.ding5_message_button_offset_y
            pyautogui.click(x=offset_x, y=offset_y)

        pyperclip.copy(contact_name)
        time.sleep(0.5)
        self.clean_search_input(app_index, search_input_x, search_input_y)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')

        time.sleep(Config.search_contact_interval)
        flag = self.contact_exists(current_app_type, contact_region)

        if not flag:
            time.sleep(Config.search_contact_interval)
            flag = self.contact_exists(current_app_type, contact_region)

        logging.info('search contact %s' % flag)

        if flag:
            if current_app_type == Config.app_type_qq:
                self.test_moved(app_index, pyautogui.doubleClick, search_input_x, search_input_y + search_target_offset)
            elif current_app_type == Config.app_type_51job:
                time.sleep(1)
                pyautogui.click(search_input_x, search_input_y + search_target_offset)
            else:
                self.test_moved(app_index, pyautogui.click, search_input_x, search_input_y + search_target_offset)
            self.current_contact[app_index] = contact_name
            self.find_logo_count[app_index] = 0
            self.find_logo_flag[app_index] = 0
            self.window_change_state[app_index] = True
            if current_app_type in (Config.app_type_whatsapp, Config.app_type_line):
                self.clean_search_input(app_index, search_input_x, search_input_y)
            return True
        else:
            self.black_list[app_index].add(contact_name)
            if current_app_type == Config.app_type_weibo:
                self.clean_search_input(app_index, search_input_x, search_input_y)
            else:
                self.test_moved(app_index, pyautogui.click, input_center_x, input_center_y)
            return False

    def clean_search_input(self, i, search_input_x, search_input_y):
        self.test_moved(i, pyautogui.moveTo, search_input_x, search_input_y)
        pyautogui.click(clicks=2, x=search_input_x, y=search_input_y, interval=0.25)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('backspace')

    def contact_exists(self, current_app_type, contact_region):
        if current_app_type == Config.app_type_momo:
            return True

        if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
            yes_contact_icon = Config.yes_contact_images[current_app_type]
            contact_region_image = autogui.screenshot().crop(self.region_to_diagonal(contact_region))
            pos_result = screen_util.locate_one(yes_contact_icon, contact_region_image)
            if pos_result is None:
                yes_group_icon = Config.yes_group_images[current_app_type]
                pos_result = screen_util.locate_one(yes_group_icon, contact_region_image)
            if pos_result is None:
                wechat_public_account_icon = Config.yes_wechat_public_bin_images
                pos_result = screen_util.locate_one(wechat_public_account_icon, contact_region_image)
            if pos_result is not None:
                return True
        elif current_app_type in (Config.app_type_qq, Config.app_type_qq_full):
            screenshot = autogui.screenshot()
            yes_contact_icon = Config.yes_contact_images[current_app_type]
            search_region = (contact_region[0], contact_region[1], contact_region[2] / 2, contact_region[3] / 5)

            pos_result = screen_util.locate_one(yes_contact_icon, screenshot, region=search_region)
            if pos_result is not None:
                return True
            yes_group_icon = Config.yes_group_images[current_app_type]
            pos_result = screen_util.locate_one(yes_group_icon, screenshot, region=search_region)
            if pos_result is not None:
                return True
        elif current_app_type in (Config.app_type_ding6, Config.app_type_line):
            yes_contact_icon = Config.yes_contact_images[current_app_type]
            contact_region_image = autogui.screenshot().crop(self.region_to_diagonal(contact_region))
            pos_result = screen_util.locate_one(yes_contact_icon, contact_region_image)
            if pos_result is not None:
                return True
            yes_contact_icon = Config.ding6_prompt_images[Config.scale_ratio_index]
            pos_result = screen_util.locate_one(yes_contact_icon, contact_region_image)
            if pos_result is not None:
                return True
        elif current_app_type == Config.app_type_51job:
            pyautogui.press('enter')
            return True
        else:
            no_contact_icon = Config.no_contact_bin_images[current_app_type]
            contact_region_image = autogui.screenshot().crop(self.region_to_diagonal(contact_region))
            pos_result = screen_util.locate_one(no_contact_icon, contact_region_image)
            if pos_result is None:
                return True
        return False

    def init_cross(self, length, bg_color, cross_color):
        result = []
        half = int(length / 2)
        for i in range(length):
            if i == half:
                line = [cross_color] * length
            else:
                line = [bg_color] * length
                line[half] = cross_color
            result.append(line)
        return result

    def qq_contact_exits(self, i):
        length = Config.qq_cross_length
        half = int(length / 2)

        def match_cross(i, j, screen, a):
            x = j + half
            for k in range(length):
                y = i + k
                if screen[y][x] != a[k][half]:
                    return False

            y = i + half
            for k in range(length):
                x = j + k
                if screen[y][x] != a[half][k]:
                    return False
            return True

        app_region = self.conf.app_region[i]
        input_region = self.conf.input_region[i]
        contact_width = input_region[0] - app_region[0]

        if contact_width < length:
            return False
        elif contact_width < 50:
            screenshot = pyscreeze.screenshot(region=(app_region[0], app_region[1], contact_width + length, Config.qq_banner_height))
            screen = np.asarray(screenshot, dtype=int)
            mean = np.mean(screen)
            height, width = screen.shape
            if mean < 0.5:
                a = self.init_cross(length, 0, 1)
            else:
                a = self.init_cross(length, 1, 0)
            for i in range(height - length):
                for j in range(width - length, -1, -1):
                    if match_cross(i, j, screen, a):
                        return True
        else:
            return True
        return False

    @reset_position
    def rpa_timer(self, i, task_type):
        flag = True
        while flag:
            flag = self.rpa_task_timer(i, task_type)

    def rpa_task_timer(self, i, task_type):
        current_app_type = self.conf.app_type[i]
        if current_app_type == Config.app_type_qq and not self.qq_contact_exits(i):
            self.timer_disable_set.add(i)
            return
        if task_type == Config.rpa_task_monitor:
            contact_names, message = get_repeater_task(self.conf.channel_name,
                                                       Config.app_type_dict[current_app_type], self.conf.channel_user)
            images = None
            logging.info('rpa_task_monitor params: %s %s %s' % (self.conf.channel_name,
                                                       Config.app_type_dict[current_app_type], self.conf.channel_user))
            logging.info('rpa_task_monitor: %s %s %s' % (contact_names, message, images))
        else:
            contact_names, message, images = get_rpa_task(self.conf.channel_name,
                                                          Config.app_type_dict[current_app_type],
                                                          self.conf.channel_user)
            logging.info('rpa_task_timer params: %s %s %s' % (self.conf.channel_name,
                                                       Config.app_type_dict[current_app_type], self.conf.channel_user))
            logging.info('rpa_task_timer: %s %s %s' % (contact_names, message, images))

        if contact_names is None:
            if task_type == Config.rpa_task_monitor:
                self.last_repeater_time[i] = time.time()
            else:
                self.last_timer_time[i] = time.time()
            if Config.timer_wait_time < Config.max_timer_wait_time:
                Config.timer_wait_time = Config.timer_wait_time << 1
            return False
        else:
            Config.timer_wait_time = 1
        input_region = self.conf.input_region[i]
        if current_app_type == Config.app_type_whatsapp:
            input_center_x, input_center_y = input_region[0] + input_region[2] / 2, input_region[1] + input_region[3]/2
        else:
            input_center_x, input_center_y = self.conf.send_btn_pos[i][0], \
                                             self.conf.send_btn_pos[i][1] - Config.input_click_offset

        if current_app_type == Config.app_type_51job:
            send_x, send_y = input_region[0] + input_region[2] - Config.send_button_offset[current_app_type][0], \
                             input_region[1] + Config.send_button_offset[current_app_type][1]
        else:
            send_x, send_y = input_region[0] + input_region[2] - Config.send_button_offset[current_app_type][0], \
                         input_region[1] + input_region[3] - Config.send_button_offset[current_app_type][1]

        input_center_x, input_center_y = autogui.get_abs_region((input_center_x, input_center_y))
        send_x, send_y = autogui.get_abs_region((send_x, send_y))

        image_dict = {}
        for contact in contact_names:
            if contact in self.black_list[i]:
                continue
            if self.current_contact[i] != contact or \
                    time.time() - self.last_search_contact_time[i] > Config.contact_wait_time:
                self.last_search_contact_time[i] = time.time()
                if not self.search_contact(contact, current_app_type, i):
                    continue

            if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
                self.click_wechat_public_btn(input_region)

            if current_app_type in (Config.app_type_weibo, Config.app_type_whatsapp):
                self.timer_send_weibo_message(i, input_center_x, input_center_y, task_type,
                                              images, image_dict, send_x, send_y, message)
            else:
                self.timer_send_message(i, input_center_x, input_center_y, task_type,
                                        images, image_dict, send_x, send_y, message)
        return True

    @synchronized
    def click_wechat_public_btn(self, input_region):
        wechat_public_btn = Config.wechat_public_btn_image[Config.scale_ratio_index]
        pos_result = pyautogui.locateOnScreen(wechat_public_btn, region=input_region)
        if pos_result is not None:
            pos = pyautogui.center(pos_result)
            pyautogui.click(pos.x, pos.y)

    @synchronized
    def timer_send_message(self, i, input_center_x, input_center_y, task_type,
                           images, image_dict, send_x, send_y, message):
        if not self.topmost_check(i):
            return
        current_app_type = self.conf.app_type[i]
        self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('backspace')
        if task_type == Config.rpa_task_timer and (platform == "win32" or platform == "linux"):
            for image_name in images:
                if image_name not in image_dict:
                    image_dict[image_name] = get_rpa_task_image(self.conf.channel_name, image_name,
                                                                self.conf.channel_user)
                send_to_clipboard(image_dict[image_name])
                time.sleep(2.5)
                self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1.5)
                if current_app_type == Config.app_type_momo:
                    time.sleep(3)
                    self.test_moved(i, pyautogui.click, send_x, send_y)
                    pyautogui.click(input_center_x, input_center_y)
                if current_app_type == Config.app_type_weibo:
                    time.sleep(3)
                    btn_list = list(pyautogui.locateAllOnScreen(Config.weibo_send_image_button))
                    if len(btn_list) > 0:
                        btn_center = pyautogui.center(btn_list[0])
                        pyautogui.click(btn_center.x, btn_center.y)
                    pyautogui.click(input_center_x, input_center_y)
        if Config.default_flag:
            message = Config.default_msg
        pyperclip.copy(message)
        time.sleep(1)
        self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
        pyautogui.hotkey('ctrl', 'v')

        if current_app_type == Config.app_type_momo:
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'enter')
        elif current_app_type in (Config.app_type_weibo, Config.app_type_whatsapp, Config.app_type_line):
            time.sleep(0.1)
            pyautogui.press('enter')
        elif current_app_type == Config.app_type_ding6:
            time.sleep(0.5)
            pyautogui.click(send_x + Config.ding6_send_button_offset, send_y)
        else:
            time.sleep(0.1)
            pyautogui.click(send_x, send_y)
            pyautogui.moveTo(10, 10)
        pyautogui.click(input_center_x, input_center_y)

        if current_app_type == Config.app_type_51job:
            search_x_offset, search_y_offset, search_target_offset = Config.rpa_timer_offset[current_app_type]
            contact_region = self.conf.contact_region[i]
            search_input_x, search_input_y = contact_region[0] + search_x_offset, contact_region[1] + search_y_offset
            self.clean_search_input(i, search_input_x, search_input_y)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.click(search_input_x, search_input_y + search_target_offset)

    def timer_send_weibo_message(self, i, input_center_x, input_center_y, task_type,
                                 images, image_dict, send_x, send_y, message):
        @synchronized
        def clear_input():
            if not self.topmost_check(i):
                return
            self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('backspace')

        @synchronized
        def copy_image():
            if not self.topmost_check(i):
                return
            send_to_clipboard(image_dict[image_name])
            time.sleep(2.5)
            self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
            pyautogui.hotkey('ctrl', 'v')

        @synchronized
        def send_image():
            if current_app_type == Config.app_type_whatsapp:
                dial_region = self.conf.dialogue_region[i]
                region = (dial_region[0] + dial_region[2] / 3, dial_region[1], dial_region[2] / 3, dial_region[3])
                pyautogui.click(region[0] + region[2] / 2, region[1] + region[3] / 2)
                time.sleep(0.2)
                pyautogui.press('enter')
                return
            app_region = self.conf.app_region[i]
            region = (app_region[0] + app_region[2]/3, app_region[1], app_region[2]/3, app_region[3])
            pyautogui.click(region[0] + region[2] / 2, region[1] + region[3] / 2)
            time.sleep(0.2)
            btn_list = list(pyautogui.locateAllOnScreen(Config.weibo_send_image_button, region=region))
            if len(btn_list) > 0:
                btn_center = pyautogui.center(btn_list[0])
                pyautogui.click(btn_center.x, btn_center.y)
            pyautogui.click(input_center_x, input_center_y)

        @synchronized
        def send_message():
            if not self.topmost_check(i):
                return
            pyperclip.copy(message)
            time.sleep(1)
            self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')
            pyautogui.click(input_center_x, input_center_y)

        current_app_type = self.conf.app_type[i]
        clear_input()
        if task_type == Config.rpa_task_timer and (platform == "win32" or platform == "linux"):
            for image_name in images:
                if image_name not in image_dict:
                    image_dict[image_name] = get_rpa_task_image(self.conf.channel_name, image_name, self.conf.channel_user)
                copy_image()
                if current_app_type == Config.app_type_weibo:
                    time.sleep(4)
                else:
                    time.sleep(2)
                send_image()
        if Config.default_flag:
            message = Config.default_msg
        send_message()

    @synchronized
    @reset_position
    def change_diag_window(self, i):
        if not self.topmost_check(i):
            return
        current_app_type = self.conf.app_type[i]
        if current_app_type == Config.app_type_qq:
            app_region = self.conf.app_region[i]
            input_region = self.conf.input_region[i]
            contact_width = input_region[0] - app_region[0]

            if contact_width < Config.qq_cross_length:
                return

        contact_region = self.conf.contact_region[i]
        screenshot = autogui.screenshot()
        if current_app_type == Config.app_type_51job:
            right_contact_region = [contact_region[0] + contact_region[2]/2, contact_region[1],
                                    contact_region[2]/2, contact_region[3]]
            red_dots = find_new_message(screenshot, right_contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.blue_index)
        elif current_app_type in (Config.app_type_whatsapp, Config.app_type_line):
            red_dots = find_new_message(screenshot, contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.green_index)
        elif current_app_type == Config.app_type_weibo:
            red_dots = find_new_message(screenshot, contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.orange_index)
        else:
            red_dots = find_new_message(screenshot, contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.red_index)
        image_data = np.asarray(screenshot)
        for j in range(len(red_dots)):
            x, y = int(red_dots[j][0]), int(red_dots[j][1])
            if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
                if not red_dot_vertical_valid(image_data, x, y):
                    continue
                if not red_dot_horizontal_valid(image_data, x, y):
                    continue
            elif current_app_type == Config.app_type_line:
                contact_x, contact_y, width, height = contact_region
                if x - contact_x < width / 2 or height - (y - contact_y) < Config.line_new_dial_offset:
                    continue
            else:
                contact_x, contact_y, width, height = contact_region
                if x - contact_x < width / 2:
                    continue
            x, y = autogui.get_abs_region((x, y))
            logging.info('red dot pos %d, %d' % (x, y))
            if current_app_type in (Config.app_type_qq, Config.app_type_qq_full):
                self.test_moved(i, pyautogui.click, x - 30, y - 10)
            elif current_app_type == Config.app_type_whatsapp:
                self.test_moved(i, pyautogui.click, x - 60, y)
            else:
                self.test_moved(i, pyautogui.click, x, y)
            self.find_logo_count[i] = 0
            self.find_logo_flag[i] = 0
            self.current_contact[i] = '$red_dot$'
            self.window_change_state[i] = True
            break
        self.window_change_state[i] = False

    def valid_red_dot_exists(self, i):
        contact_region = self.conf.contact_region[i]
        current_app_type = self.conf.app_type[i]
        screenshot = autogui.screenshot()
        if current_app_type == Config.app_type_51job:
            right_contact_region = [contact_region[0] + contact_region[2] / 2, contact_region[1], contact_region[2] / 2, contact_region[3]]
            red_dots = find_new_message(screenshot, right_contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.blue_index)
        elif current_app_type in (Config.app_type_whatsapp, Config.app_type_line):
            red_dots = find_new_message(screenshot, contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.green_index)
        else:
            red_dots = find_new_message(screenshot, contact_region, self.red_dot_array, self.red_index, self.red_count, AiConfig.red_index)
        current_app_type = self.conf.app_type[i]

        screenshot = autogui.screenshot()
        image_data = np.asarray(screenshot, dtype=int)
        for j in range(len(red_dots)):
            x, y = int(red_dots[j][0]), int(red_dots[j][1])
            if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
                if red_dot_vertical_valid(image_data, x, y):
                    return True
                if not red_dot_horizontal_valid(image_data, x, y):
                    return True
            elif current_app_type == Config.app_type_line:
                contact_x, contact_y, width, height = contact_region
                if x - contact_x > width / 2 and height - (y - contact_y) > Config.line_new_dial_offset:
                    return True
            else:
                contact_x, contact_y, width, height = contact_region
                if x - contact_x > width / 2:
                    return True
        return False

    def update_dial_check_lines(self, i, size, screenshot, dialogue_region):
        self.dial_check_lines[i] = []
        width, height = dialogue_region[2], dialogue_region[3]
        dial_x_min, dial_y_min = dialogue_region[0], dialogue_region[1]
        step_x, step_y = int(width / size), int(height / size)
        for j in range(1, size):
            x, y = dial_x_min + step_x * j, dial_y_min
            line_width, line_height = 1, height
            x2, y2 = x + line_width, y + line_height
            line_image = screenshot.crop((x, y, x2, y2))
            line = {'line_region': (x, y, line_width, line_height), 'line_image': line_image}
            self.dial_check_lines[i].append(line)

        for j in range(1, size):
            x, y = dial_x_min, dial_y_min + step_y * j
            line_width, line_height = width, 1
            x2, y2 = x + line_width, y + line_height
            line_image = screenshot.crop((x, y, x2, y2))
            line = {'line_region': (x, y, line_width, line_height), 'line_image': line_image}
            self.dial_check_lines[i].append(line)

    def dial_lines_is_changed(self, i, screenshot):
        dial_check_lines = self.dial_check_lines[i]
        if len(dial_check_lines) == 0:
            return True
        for j in range(len(dial_check_lines)):
            line_region = dial_check_lines[j]['line_region']
            line_image = dial_check_lines[j]['line_image']
            pos_result = pyautogui.locate(line_image, screenshot, region=line_region, grayscale=True)
            if pos_result is None:
                return True
        return False

    def update_repeater_check_lines(self, i, size, screenshot, dialogue_region):
        self.repeater_check_lines[i] = []
        width, height = dialogue_region[2], dialogue_region[3]
        dial_x_min, dial_y_min = dialogue_region[0], dialogue_region[1]
        step_x, step_y = int(width / size), int(height / size)
        for j in range(1, size):
            x, y = dial_x_min + step_x * j, dial_y_min
            line_width, line_height = 1, height
            x2, y2 = x + line_width, y + line_height
            line_image = screenshot.crop((x, y, x2, y2))
            line = {'line_region': (x, y, line_width, line_height), 'line_image': line_image}
            self.repeater_check_lines[i].append(line)

        for j in range(1, size):
            x, y = dial_x_min, dial_y_min + step_y * j
            line_width, line_height = width, 1
            x2, y2 = x + line_width, y + line_height
            line_image = screenshot.crop((x, y, x2, y2))
            line = {'line_region': (x, y, line_width, line_height), 'line_image': line_image}
            self.repeater_check_lines[i].append(line)

    def repeater_lines_is_changed(self, i, screenshot):
        check_lines = self.repeater_check_lines[i]
        if len(check_lines) == 0:
            return True
        for j in range(len(check_lines)):
            line_region = check_lines[j]['line_region']
            line_image = check_lines[j]['line_image']
            pos_result = pyautogui.locate(line_image, screenshot, region=line_region, grayscale=True)
            if pos_result is None:
                return True
        return False

    def find_message(self, screenshot, dialogue_region, current_app_type):
        if current_app_type in (Config.app_type_whatsapp, Config.app_type_line):
            logo_x, logo_y, my_message_exists = find_message_no_logo(screenshot, dialogue_region, current_app_type)
        else:
            logo_x, logo_y, my_message_exists = find_logo(screenshot, dialogue_region, current_app_type, self.app_idx)
        return logo_x, logo_y, my_message_exists

    @reset_position
    def auto(self, i, contact=None):
        # 四个值分别为x, y, w, h
        dialogue_region = self.conf.dialogue_region[i]
        input_region = self.conf.input_region[i]
        current_app_type = self.conf.app_type[i]

        if current_app_type in (Config.app_type_wechat, Config.app_type_wechat_gray):
            self.click_wechat_public_btn(input_region)

        if self.find_logo_flag[i] == 0:
            screenshot = autogui.screenshot().convert('L')
            if not self.window_change_state[i]:
                time.sleep(0.374)
                if self.dial_lines_is_changed(i, screenshot):
                    logo_x, logo_y, my_message_exists = self.find_message(screenshot, dialogue_region, current_app_type)
                else:
                    logo_x, logo_y = -1, -1
                    my_message_exists = False
                    time.sleep(0.128)
            else:
                logo_x, logo_y, my_message_exists = self.find_message(screenshot, dialogue_region, current_app_type)

            if logo_x != -1 and my_message_exists and current_app_type not in (Config.app_type_whatsapp, Config.app_type_line):
                self.find_logo_flag[i] = 1
                self.find_logo_count[i] = 0
        else:
            if current_app_type == Config.app_type_weibo:
                time.sleep(0.256)
            screenshot = autogui.screenshot().convert('L')
            logo_x, logo_y = fast_logo(screenshot, dialogue_region, self.app_idx)
            self.find_logo_count[i] = self.find_logo_count[i] + 1
            if logo_x == 0 or self.find_logo_count[i] > Config.find_logo_random:
                self.find_logo_count[i] = 0
                self.find_logo_flag[i] = 0
                return

        logging.info('logo pos %s, %s' % (logo_x, logo_y))

        if logo_x == -1:
            self.update_dial_check_lines(i, 4, screenshot, dialogue_region)
            return

        if current_app_type == Config.app_type_whatsapp:
            dial_x, dial_y = int(logo_x + 20 * Config.scale_ratio), int(logo_y + Config.logo_offset_y - 20 * Config.scale_ratio)
        elif current_app_type == Config.app_type_line:
            dial_x, dial_y = int(logo_x + 20 * Config.scale_ratio), int(logo_y + Config.logo_offset_y - 20 * Config.scale_ratio)
        else:
            dial_x, dial_y = logo_x + Config.logo_offset_x, logo_y + Config.logo_offset_y

        if not self.abort:
            cursor_type = self.get_mouse_cursor_type(i, dial_x, dial_y)
            question, answer = '', '已收到~'
            if cursor_type == Config.mouse_cursor_text or cursor_type == Config.mouse_cursor_normal:
                question = self.copy_question(dial_x, dial_y, dialogue_region, i)
                if question == '':
                    return
                if contact is not None:
                    if contact['id'] not in self.last_repeater_message[i] or self.last_repeater_message[i][contact['id']] != question:
                        message_dict = {'appId': Config.app_type_dict[current_app_type], 'channelName': self.conf.channel_name,
                                        'contactId': contact['id'], 'message': question, 'channelUser': self.conf.channel_user}
                        add_repeater_message(message_dict)
                        self.last_repeater_message[i][contact['id']] = question
                    if self.conf.rpa_robot_flag == 0:
                        return
                if self.last_question[i] == question:
                    return
                logging.info('question: ' + question)
                answer = qa_call(question, self.conf.channel_name, self.conf.channel_user)
            if answer == '' or answer == 'null':
                return

        input_center_x = self.conf.send_btn_pos[i][0]
        input_center_y = self.conf.send_btn_pos[i][1] - Config.input_click_offset
        if current_app_type == Config.app_type_51job:
            send_x, send_y = input_region[0] + input_region[2] - Config.send_button_offset[current_app_type][0], \
                             input_region[1] + Config.send_button_offset[current_app_type][1]
        else:
            send_x, send_y = input_region[0] + input_region[2] - Config.send_button_offset[current_app_type][0], \
                             input_region[1] + input_region[3] - Config.send_button_offset[current_app_type][1]

        input_center_x, input_center_y = autogui.get_abs_region((input_center_x, input_center_y))
        send_x, send_y = autogui.get_abs_region((send_x, send_y))

        if not self.abort:
            self.send_robot_message(i, input_center_x, input_center_y, send_x, send_y, answer)

        screenshot = autogui.screenshot().convert('L')
        self.update_dial_check_lines(i, 4, screenshot, dialogue_region)

    @synchronized
    def send_robot_message(self, i, input_center_x, input_center_y, send_x, send_y, answer):
        if not self.topmost_check(i):
            return
        current_app_type = self.conf.app_type[i]
        self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
        if Config.default_flag:
            answer = Config.default_msg
        pyperclip.copy(answer)
        time.sleep(0.5)
        self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
        pyautogui.hotkey('ctrl', 'v')
        if self.conf.app_type[i] in (Config.app_type_weibo, Config.app_type_whatsapp, Config.app_type_line):
            time.sleep(0.5)
            self.test_moved(i, pyautogui.press, 'enter')
        elif current_app_type == Config.app_type_ding6:
            time.sleep(0.5)
            self.test_moved(i, pyautogui.click, send_x + Config.ding6_send_button_offset, send_y)
        else:
            time.sleep(0.5)
            self.test_moved(i, pyautogui.click, send_x, send_y)
            pyautogui.moveTo(10, 10)

        self.test_moved(i, pyautogui.click, input_center_x, input_center_y)
        # self.last_question[i] = question
        self.last_qa_time[i] = time.time()
        logging.info('answer: ' + answer)

    @synchronized
    def get_mouse_cursor_type(self, i, dial_x, dial_y):
        if not self.topmost_check(i):
            return Config.mouse_cursor_text
        self.test_moved(i, pyautogui.moveTo, dial_x, dial_y)

        if platform == "win32":
            import win32gui
            cursor_type = win32gui.GetCursorInfo()[1]
            if cursor_type == Config.windows_cursor_text:
                return Config.mouse_cursor_text
            elif cursor_type == Config.window_cursor_link:
                return Config.mouse_cursor_link
            elif cursor_type == Config.windows_cursor_normal:
                return Config.mouse_cursor_normal
        return Config.mouse_cursor_text

    @synchronized
    def copy_question(self, dial_x, dial_y, dialogue_region, i):
        if not self.topmost_check(i):
            return ''
        app_type = self.conf.app_type[i]
        if app_type == Config.app_type_51job:
            logo_x, logo_y = dial_x - Config.logo_offset_x, dial_y - Config.logo_offset_y + 20
            drag_end_y = self.conf.input_region[i][1] + 30
            pyautogui.moveTo(logo_x, logo_y)
            self.test_moved(i, pyautogui.dragTo, logo_x, drag_end_y, 1.5, button='left')
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            question = pyperclip.paste().strip()
            return question

        dial_x, dial_y = autogui.get_abs_region((dial_x, dial_y))

        self.test_moved(i, pyautogui.click, x=dial_x, y=dial_y)
        if app_type not in (Config.app_type_ding6, Config.app_type_whatsapp, Config.app_type_line):
            self.test_moved(i, pyautogui.click, button='right', x=dial_x, y=dial_y)
        if app_type in (Config.app_type_ding, Config.app_type_ding_gray, Config.app_type_ding_full):
            copy_menu_search_region = (
                dialogue_region[0], dialogue_region[1], dialogue_region[2] * 0.6, dialogue_region[3])
            pos_list = list(
                pyautogui.locateAllOnScreen(Config.ding_copy, region=copy_menu_search_region, grayscale=True))
            center_pos = pyautogui.center(pos_list[0])
            self.test_moved(i, pyautogui.click, x=center_pos.x, y=(center_pos.y + 5))
        elif app_type in (Config.app_type_qq, Config.app_type_qq_full):
            time.sleep(0.5)
            self.test_moved(i, pyautogui.press, 'c')
        elif app_type == Config.app_type_ding6:
            self.test_moved(i, pyautogui.click, x=dial_x, y=dial_y, clicks=3)
            pyautogui.hotkey('ctrl', 'c')
        elif app_type == Config.app_type_whatsapp:
            self.test_moved(i, pyautogui.click, x=dial_x, y=dial_y, clicks=3)
            pyautogui.hotkey('ctrl', 'c')
        elif app_type == Config.app_type_line:
            self.test_moved(i, pyautogui.click, x=dial_x, y=dial_y, clicks=3)
            pyautogui.hotkey('ctrl', 'c')
        else:
            x = dial_x + Config.copy_offset_x
            y = dial_y + Config.copy_offset_y
            self.test_moved(i, pyautogui.click, x=x, y=y)

        time.sleep(0.05)
        question = pyperclip.paste().strip()
        return question
