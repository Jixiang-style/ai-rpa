#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.


# gui.py

# Copyright (C) 2020 Beijing Landing Technologies, China


# cython: language_level=3
import json
import logging
import os
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from sys import platform
from tkinter import Tk, Label, Button, Canvas, StringVar, Entry, messagebox, LEFT, CENTER, SOLID, GROOVE, Frame, NW

import mss
import numpy as np
import pyautogui as pg
from PIL import Image, ImageTk, ImageFilter
from ai.config import AiConfig
from ai.image import find_edge, image_binarize

from landingbj import app_detect, autogui
from landingbj.config import Config
from landingbj.message_box import DialCheckMessagebox
from landingbj.resource_sync import ResourceSync
from landingbj.rpa import RpaProcess
from landingbj.setting_frame import SettingTabFrame, ROBOT_TAB_NAME, TIMER_TAB_NAME, REPEATER_TAB_NAME
from landingbj.util import get_current_settings


class Screen(Tk):
    def __init__(self, main, image):
        Tk.__init__(self)
        self.x = self.y = 0
        self.canvas = Canvas(self, width=512, height=512, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.red_rect = []
        self.blue_rect = []
        self.start_x = self.start_y = self.curX = self.curY = 0
        self.master = main
        self.rect_num = 0
        self.im = image
        self._draw_image()

        self.geometry(self.master.master.geometry())
        self.overrideredirect(True)
        self.state("zoomed")

    def _draw_image(self):
        self.tk_im = ImageTk.PhotoImage(self.im, master=self.canvas)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)

        app_region = self.master.config.app_region
        input_region = self.master.config.input_region

        for i in range(len(input_region)):
            start_x, start_y = input_region[i][0], input_region[i][1]
            end_x, end_y = input_region[i][0] + input_region[i][2], input_region[i][1] + input_region[i][3]
            rectangle_options = {'dash': (5, 5), 'outline_color': 'blue'}
            rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, dash=rectangle_options['dash'],
                                                outline=rectangle_options['outline_color'], width=2)
            self.canvas.coords(rect, start_x, start_y, end_x, end_y)

        for i in range(len(app_region)):
            start_x, start_y = app_region[i][0], app_region[i][1]
            end_x, end_y = app_region[i][0] + app_region[i][2], app_region[i][1] + app_region[i][3]
            rectangle_options = {'dash': (5, 5), 'outline_color': 'red'}
            rect = self.canvas.create_rectangle(start_x, start_y, end_x, end_y, dash=rectangle_options['dash'],
                                                outline=rectangle_options['outline_color'], width=2)
            self.canvas.coords(rect, start_x, start_y, end_x, end_y)

        self.edge_data = np.asarray(self.im.convert('L').filter(ImageFilter.FIND_EDGES))

    def on_button_press(self, event):
        if self.master.btn_app_pos['state'] == 'normal':
            return

        if self.rect_num > 1:
            self.master.prompt_index = 1
            self.master.button_label['text'] = self.master.prompt_msg[self.master.prompt_index]
            self.master.button_label['foreground'] = 'red'
            self.clear_last()

        if self.rect_num != 1:
            rectangle_options = {'dash': (5, 5), 'outline_color': 'red'}
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, dash=rectangle_options['dash'],
                                                     outline=rectangle_options['outline_color'], width=2)
            self.blue_rect.append(self.rect)
            self.master.save_btn['state'] = 'disabled'
        else:
            rectangle_options = {'dash': (5, 5), 'outline_color': 'blue'}
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, dash=rectangle_options['dash'],
                                                     outline=rectangle_options['outline_color'], width=2)
            self.red_rect.append(self.rect)

        self.start_x = event.x
        self.start_y = event.y

    def on_move_press(self, event):
        if self.master.btn_app_pos['state'] == 'normal':
            return
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        if self.master.btn_app_pos['state'] == 'normal':
            return
        self.curX, self.curY = (event.x, event.y)
        self.start_x, self.start_y, self.curX, self.curY = find_edge(self.edge_data, self.get_region())
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
        self.rect_num = self.rect_num + 1
        if self.rect_num == 1:
            self.master.prompt_index = 2
            self.master.button_label['fg'] = 'blue'
            self.master.config.app_region.append(self.get_region())
        elif self.rect_num == 2:
            self.master.prompt_index = 3
            self.master.button_label['fg'] = 'black'
            self.master.config.input_region.append(self.get_region())
            self.master.save_btn['state'] = 'normal'
            self.master.save_btn['image'] = self.master.save_icon
            self.master.save_btn['command'] = self.master.save
        self.master.button_label['text'] = self.master.prompt_msg[self.master.prompt_index]

    def get_region(self):
        xl = self.start_x
        yl = self.start_y
        xr = self.curX
        yr = self.curY
        if xl > xr:
            xl, xr = xr, xl
        if yl > yr:
            yl, yr = yr, yl

        width = xr - xl
        height = yr - yl
        region = (xl, yl, width, height)
        return region

    def clear_all(self):
        for i in self.red_rect:
            self.canvas.delete(i)
        for i in self.blue_rect:
            self.canvas.delete(i)

    def clear_last(self):
        self.canvas.delete(self.red_rect[-1])
        self.canvas.delete(self.blue_rect[-1])
        self.master.config.app_region.pop()
        self.master.config.input_region.pop()
        self.red_rect.pop()
        self.blue_rect.pop()
        self.rect_num = 0


class Main:
    def __init__(self, master, conf):
        self.config = conf
        self.master = master

        dpi_value = self.master.winfo_fpixels('1i')
        Config.scale_ratio = round(dpi_value / 96.0, 2)
        Config.send_button_offset_left = Config.send_button_offset_left * Config.scale_ratio
        Config.send_button_offset_up = Config.send_button_offset_up * Config.scale_ratio
        Config.logo_offset_x = Config.logo_offset_x * Config.scale_ratio
        Config.logo_offset_y = Config.logo_offset_y * Config.scale_ratio
        Config.ding5_message_button_offset_x = Config.ding5_message_button_offset_x * Config.scale_ratio
        Config.ding5_message_button_offset_y = Config.ding5_message_button_offset_y * Config.scale_ratio
        Config.input_icon_offset[0] = Config.input_icon_offset[0] * Config.scale_ratio
        Config.input_icon_offset[1] = Config.input_icon_offset[1] * Config.scale_ratio
        Config.line_new_dial_offset = Config.line_new_dial_offset * Config.scale_ratio
        AiConfig.line_seed_x_start = int(AiConfig.line_seed_x_start * Config.scale_ratio)
        AiConfig.line_seed_x_length = int(AiConfig.line_seed_x_length * Config.scale_ratio)
        AiConfig.whatsapp_seed_x_start = int(AiConfig.whatsapp_seed_x_start * Config.scale_ratio)
        Config.input_click_offset = Config.input_click_offset * Config.scale_ratio

        if Config.scale_ratio == 1.50:
            Config.red_round_size = 21
        elif Config.scale_ratio == 1.25:
            Config.red_round_size = 17

        logging.info('screen scale ratio %s' % Config.scale_ratio)

        for i in range(len(Config.rpa_timer_offset)):
            a = Config.rpa_timer_offset[i][0] * Config.scale_ratio
            b = Config.rpa_timer_offset[i][1] * Config.scale_ratio
            c = Config.rpa_timer_offset[i][2] * Config.scale_ratio
            Config.rpa_timer_offset[i] = (a, b, c)

        for i in range(len(Config.search_point_offset)):
            for j in range(len(Config.search_point_offset[i])):
                Config.search_point_offset[i][j] = Config.search_point_offset[i][j] * Config.scale_ratio

        for i in range(len(Config.title_offset)):
            Config.title_offset[i] = Config.title_offset[i] * Config.scale_ratio

        for i in range(len(Config.app_min_region)):
            for j in range(len(Config.app_min_region[i])):
                for k in range(len(Config.app_min_region[i][j])):
                    Config.app_min_region[i][j][k] = Config.app_min_region[i][j][k] * Config.scale_ratio

        for i in range(len(Config.send_button_offset)):
            if i in (Config.app_type_ding6, ):
                continue
            for j in range(len(Config.send_button_offset[i])):
                Config.send_button_offset[i][j] = Config.send_button_offset[i][j] * Config.scale_ratio

        if platform == "darwin":
            self.init_width, self.init_height = 232, 365
        elif platform == 'linux':
            self.init_width, self.init_height = 232, 365
        else:
            self.init_width, self.init_height = 232, 365

        self.init_width = self.init_width * Config.scale_ratio
        self.init_height = self.init_height * Config.scale_ratio
        init_pos_x = 300
        init_pos_y = 300
        self.master.geometry('%dx%d+%d+%d' % (self.init_width, self.init_height, init_pos_x, init_pos_y))

        self.master.resizable(0, 0)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.prompt_msg = [' 请点击“校准”获取软件区域', ' 拖动鼠标获取目标软件边界', ' 拖动鼠标获取其输入框位置',
                           ' 请点击“保存”记忆当前设定', ' 请点击“结束”停止自动状态']
        self.prompt_index = 0
        self.prompt_msg_label = None
        self.init_main_frame()
        self.init_function_frame()
        self.init_channel_frame()
        self.init_rpa_frame()
        self.master.call("wm", "attributes", ".", "-topmost", "true")
        self.screen_running = False
        self.screen = None
        self.rpa = None
        self.rpa_list = None
        self.pool = ThreadPoolExecutor(max_workers=16)
        self.setting_frame_status = 0

        resource_sync = ResourceSync()
        resource_sync.start()

        # DialCheckMessagebox(self.master)
        # LoginMessagebox(self.master)
        # self.open_rpa_setting()

    def init_main_frame(self):
        self.main_frame = Frame(self.master, bg='white', borderwidth=0)
        self.main_frame.pack()
        self.main_frame.place(x=0, y=0, width=self.init_width, height=self.init_height)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=154)
        self.main_frame.rowconfigure(1, weight=100)
        self.main_frame.rowconfigure(2, weight=156)

    def init_function_frame(self):
        btn_width = int(55 * Config.scale_ratio)
        btn_height = int(55 * Config.scale_ratio)
        finger_width = int(13.5 * Config.scale_ratio)
        finger_height = int(10.5 * Config.scale_ratio)
        self.button_label_frame = Frame(self.main_frame, borderwidth=1)
        self.button_label_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        self.button_label_frame.columnconfigure(0, weight=1)
        self.button_label_frame.columnconfigure(1, weight=1)
        self.button_label_frame.columnconfigure(2, weight=1)
        self.button_label_frame.rowconfigure(0, weight=1)

        self.label_padx = int(16 * Config.scale_ratio)
        self.btn_padx = int(19 * Config.scale_ratio)

        icon = Image.open(self.config.pos_icon).resize((btn_width, btn_height), Image.ANTIALIAS)
        self.pos_icon = ImageTk.PhotoImage(icon)
        self.btn_app_pos = Button(self.button_label_frame, image=self.pos_icon, borderwidth=0, height=btn_height,
                                  width=btn_width, command=lambda: self.btn_app_pos_action(1))
        if platform == "darwin":
            self.btn_app_pos.grid(row=0, column=0, columnspan=1, pady=(5, 5), padx=(self.label_padx, 5))
        else:
            self.btn_app_pos.grid(row=0, column=0, columnspan=1, pady=(5, 5), sticky='W', padx=(self.btn_padx, 16))

        icon = Image.open(self.config.start_icon).resize((btn_width, btn_height), Image.ANTIALIAS)
        self.start_icon = ImageTk.PhotoImage(icon)
        self.btn_start = Button(self.button_label_frame, compound=LEFT, image=self.start_icon, height=btn_height,
                                width=btn_width, state='disabled', borderwidth=0, command=self.rpa_start)
        if platform == "darwin":
            self.btn_start.grid(row=0, column=1, pady=(5, 5), padx=5)
        else:
            self.btn_start.grid(row=0, column=1, pady=(5, 5))

        icon = Image.open(self.config.save_icon).resize((btn_width, btn_height), Image.ANTIALIAS)
        self.save_icon = ImageTk.PhotoImage(icon)
        self.save_btn = Button(self.button_label_frame, compound=LEFT, image=self.save_icon, borderwidth=0,
                               height=btn_height, width=btn_width, state='disabled', command=self.save)
        if platform == "darwin":
            self.save_btn.grid(row=0, column=2, pady=(5, 5), padx=(5, 10))
        else:
            self.save_btn.grid(row=0, column=2, pady=(5, 5), sticky='E', padx=(16, self.btn_padx))

        icon = Image.open(self.config.finger_icon).resize((finger_width, finger_height), Image.ANTIALIAS)
        self.finger_icon = ImageTk.PhotoImage(icon)
        self.button_label = Label(self.button_label_frame, anchor='center', compound='left', image=self.finger_icon,
                                  text=self.prompt_msg[self.prompt_index], fg='red')
        self.button_label.config(font=(None, 8))
        self.button_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        icon = Image.open(self.config.reset_icon).resize((btn_width, btn_height), Image.ANTIALIAS)
        self.reset_icon = ImageTk.PhotoImage(icon)
        icon = Image.open(self.config.stop_icon).resize((btn_width, btn_height), Image.ANTIALIAS)
        self.stop_icon = ImageTk.PhotoImage(icon)

    def init_channel_frame(self):
        label_frame_padx = (int(20 * Config.scale_ratio), int(20 * Config.scale_ratio))
        self.qa_info_frame = Frame(self.main_frame, width=self.init_width, bg='#265ed7')
        self.qa_info_frame.config(borderwidth=0, relief=SOLID)
        self.qa_info_frame.grid(row=1, column=0, sticky='wens', padx=0, pady=0)
        self.qa_info_frame.columnconfigure(0, weight=1)
        self.qa_info_frame.rowconfigure(0, weight=1)
        self.qa_label_frame = Frame(self.qa_info_frame, bg='#265ed7')
        self.qa_label_frame.grid(row=0, column=0, sticky='ew', padx=label_frame_padx, pady=0)
        self.qa_label_frame.columnconfigure(0, weight=1)
        self.qa_label_frame.columnconfigure(1, weight=1)
        self.qa_label_frame.rowconfigure(0, weight=1)
        self.qa_label_frame.rowconfigure(1, weight=1)

        self.channel_name = StringVar()
        self.channel_name.set(self.config.channel_name)
        self.channel_name.trace_add("write", self.config_input_trace)
        entry_channel_name = Entry(self.qa_label_frame, textvariable=self.channel_name, borderwidth=0, fg='#f7fffa',
                                   bg='#799be3', width=10)
        entry_channel_name.grid(row=0, column=0, sticky='WE', columnspan=1, pady=(15, 0), padx=(0, 10))

        self.channel_user = StringVar()
        self.channel_user.set(self.config.channel_user)
        self.channel_user.trace_add("write", self.config_input_trace)
        entry_channel_user = Entry(self.qa_label_frame, textvariable=self.channel_user, borderwidth=0, fg='#f7fffa',
                                   bg='#799be3', width=10)
        entry_channel_user.grid(row=0, column=1, sticky='WE', columnspan=1, pady=(15, 0), padx=(10, 0))

        url = 'http://' + self.channel_name.get() + '.cloud.landingbj.com'
        self.entry_channel_domain = Label(self.qa_label_frame, text=url, bg='#265ed7', fg='white', cursor="hand2",
                                          anchor=NW, justify=LEFT)
        self.entry_channel_domain.config(font=('Helvetica', 8))
        self.entry_channel_domain.grid(row=1, column=0, sticky='NSW', columnspan=2, pady=(10, 0), padx=0)
        self.entry_channel_domain.bind("<Button-1>", self.open_url)

        self.entry_channel_line = Frame(self.qa_label_frame, height=1, relief=GROOVE,
                                        highlightthickness=1, highlightbackground="white", highlightcolor="white")
        self.entry_channel_line.grid(row=1, column=0, sticky='wes', columnspan=2)
        self.setting_btn_icon = ImageTk.PhotoImage(Image.open(Config.setting_icon))
        self.setting_btn = Button(self.qa_label_frame, image=self.setting_btn_icon, bg='#265ed7', borderwidth=0,
                                  height=25, width=25, command=lambda: self.rpa_setting())
        self.setting_btn.grid(row=1, column=1, sticky='NSE', columnspan=2, pady=(10, 0), padx=0)

    def change_switch_bg(self, choice):
        if Config.scale_ratio == 1.25:
            label_width = int(212 * Config.scale_ratio) + 5
        elif Config.scale_ratio == 1.5:
            label_width = int(212 * Config.scale_ratio) + 10
        else:
            label_width = int(212 * Config.scale_ratio)
        label_height = int(38 * Config.scale_ratio)

        self.reset_switch_bg()
        if choice == ROBOT_TAB_NAME:
            label_image = Image.open(Config.rpa_icon_robot_gray).resize((label_width, label_height), Image.ANTIALIAS)
            self.rpa_icon_robot = ImageTk.PhotoImage(label_image)
            self.robot_label['image'] = self.rpa_icon_robot
            self.robot_switch['bg'] = '#F0F0F0'
        elif choice == TIMER_TAB_NAME:
            label_image = Image.open(Config.rpa_icon_timer_gray).resize((label_width, label_height), Image.ANTIALIAS)
            self.rpa_icon_timer = ImageTk.PhotoImage(label_image)
            self.timer_label['image'] = self.rpa_icon_timer
            self.timer_switch['bg'] = '#F0F0F0'
        elif choice == REPEATER_TAB_NAME:
            label_image = Image.open(Config.rpa_icon_monitor_gray).resize((label_width, label_height), Image.ANTIALIAS)
            self.rpa_icon_monitor = ImageTk.PhotoImage(label_image)
            self.repeater_label['image'] = self.rpa_icon_monitor
            self.monitor_switch['bg'] = '#F0F0F0'

    def reset_switch_bg(self):
        label_width = int(192 * Config.scale_ratio)
        label_height = int(38 * Config.scale_ratio)
        label_image = Image.open(Config.rpa_icon_robot).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_robot = ImageTk.PhotoImage(label_image)
        self.robot_label['image'] = self.rpa_icon_robot
        self.robot_switch['bg'] = 'white'
        label_image = Image.open(Config.rpa_icon_timer).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_timer = ImageTk.PhotoImage(label_image)
        self.timer_label['image'] = self.rpa_icon_timer
        self.timer_switch['bg'] = 'white'
        label_image = Image.open(Config.rpa_icon_monitor).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_monitor = ImageTk.PhotoImage(label_image)
        self.repeater_label['image'] = self.rpa_icon_monitor
        self.monitor_switch['bg'] = 'white'

    def init_rpa_frame(self):
        label_width = int(192 * Config.scale_ratio)
        label_height = int(38 * Config.scale_ratio)
        self.switch_frame = Frame(self.main_frame, bg='#265ed7')
        self.switch_frame.grid(row=2, column=0, sticky='wens', padx=0, pady=0)
        self.switch_frame.columnconfigure(0, weight=1)
        self.switch_frame.rowconfigure(0, weight=1)
        self.rpa_label_frame = Frame(self.switch_frame, bg='#265ed7')
        self.rpa_label_frame.grid(row=0, column=0, sticky='nw', padx=(int(20 * Config.scale_ratio), 0), pady=(20, 0))
        self.rpa_label_frame.columnconfigure(0, weight=1)
        self.rpa_label_frame.rowconfigure(0, weight=1)
        self.rpa_label_frame.rowconfigure(1, weight=1)
        self.rpa_label_frame.rowconfigure(2, weight=1)

        self.rpa_switch_on = ImageTk.PhotoImage(Image.open(Config.rpa_switch_on))
        self.rpa_switch_off = ImageTk.PhotoImage(Image.open(Config.rpa_switch_off))

        label_image = Image.open(Config.rpa_icon_robot).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_robot = ImageTk.PhotoImage(label_image)
        self.robot_label = Label(self.rpa_label_frame, justify=CENTER, bg='#265ed7',
                                 compound=CENTER, image=self.rpa_icon_robot, bd=0)
        self.robot_label.grid(row=0, column=0, sticky='wns', pady=(2, 2))
        self.robot_switch = Button(self.rpa_label_frame, justify=CENTER, borderwidth=0, bg='white', fg='white',
                                   highlightthickness=0, bd=0, compound=CENTER, command=self.robot_switch_change)
        if Config.rpa_robot_flag == 0:
            self.robot_switch['image'] = self.rpa_switch_off
        else:
            self.robot_switch['image'] = self.rpa_switch_on
        self.robot_switch.grid(row=0, column=0, sticky='w', pady=(0, 0), padx=(127 * Config.scale_ratio, 0))

        label_image = Image.open(Config.rpa_icon_timer).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_timer = ImageTk.PhotoImage(label_image)
        self.timer_label = Label(self.rpa_label_frame, justify=LEFT, bg='#265ed7',
                                 compound=LEFT, image=self.rpa_icon_timer, bd=0)
        self.timer_label.grid(row=1, column=0, pady=(2, 2), sticky='wns')
        self.timer_switch = Button(self.rpa_label_frame, justify=CENTER, borderwidth=0, bg='white', fg='white',
                                   highlightthickness=0, bd=0, compound=CENTER, image=self.rpa_switch_on,
                                   command=self.timer_switch_change)
        if Config.rpa_timer_flag == 0:
            self.timer_switch['image'] = self.rpa_switch_off
        else:
            self.timer_switch['image'] = self.rpa_switch_on
        self.timer_switch.grid(row=1, column=0, sticky='w', pady=(0, 0), padx=(127 * Config.scale_ratio, 0))

        label_image = Image.open(Config.rpa_icon_monitor).resize((label_width, label_height), Image.ANTIALIAS)
        self.rpa_icon_monitor = ImageTk.PhotoImage(label_image)
        self.repeater_label = Label(self.rpa_label_frame, justify=CENTER, bg='#265ed7',
                                    compound=CENTER, image=self.rpa_icon_monitor, bd=0)
        self.repeater_label.grid(row=2, column=0, sticky='wns', pady=(2, 2))
        self.monitor_switch = Button(self.rpa_label_frame, justify=CENTER, borderwidth=0, bg='white', fg='white',
                                     highlightthickness=0, bd=0, compound=CENTER, image=self.rpa_switch_on,
                                     command=self.monitor_switch_change)
        if Config.rpa_monitor_flag == 0:
            self.monitor_switch['image'] = self.rpa_switch_off
        else:
            self.monitor_switch['image'] = self.rpa_switch_on
        self.monitor_switch.grid(row=2, column=0, sticky='w', pady=(0, 0), padx=(127 * Config.scale_ratio, 0))

    def init_setting_frame(self):
        self.master.geometry('%dx%d' % (self.init_width * 2.618, self.init_height * 1))
        self.setting_frame = SettingTabFrame(self.master, self.init_height, self.init_width * 1.618, self)
        self.setting_frame.pack()
        self.setting_frame.place(x=self.init_width, height=self.init_height, width=self.init_width * 1.618)
        # for child in self.setting_detail_frame.winfo_children():
        #     child.destroy()

    def rpa_setting(self):
        if self.setting_frame_status == 0:
            self.open_rpa_setting()
        else:
            self.close_rpa_setting()

    def open_rpa_setting(self):
        self.init_setting_frame()
        self.setting_frame_status = 1

    def close_rpa_setting(self):
        self.master.geometry('%dx%d' % (self.init_width, self.init_height))
        if self.setting_frame_status == 1:
            self.setting_frame.destroy()
        self.setting_frame_status = 0
        self.reset_switch_bg()

    def robot_switch_change(self):
        if Config.rpa_robot_flag == 1:
            self.robot_switch['image'] = self.rpa_switch_off
            Config.rpa_robot_flag = 0
        else:
            self.robot_switch['image'] = self.rpa_switch_on
            Config.rpa_robot_flag = 1
        self.save_settings()

    def timer_switch_change(self):
        if Config.rpa_timer_flag == 1:
            self.timer_switch['image'] = self.rpa_switch_off
            Config.rpa_timer_flag = 0
        else:
            self.timer_switch['image'] = self.rpa_switch_on
            Config.rpa_timer_flag = 1
        self.save_settings()

    def monitor_switch_change(self):
        if Config.rpa_monitor_flag == 1:
            self.monitor_switch['image'] = self.rpa_switch_off
            Config.rpa_monitor_flag = 0
        else:
            self.monitor_switch['image'] = self.rpa_switch_on
            Config.rpa_monitor_flag = 1
        self.save_settings()

    def save_settings(self):
        settings = get_current_settings()
        with open('config.json', 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)

    def config_input_trace(self, var, indx, mode):
        url = 'http://' + self.channel_name.get() + '.cloud.landingbj.com'
        self.entry_channel_domain['text'] = url
        self.config.channel_name = self.channel_name.get()
        self.config.channel_user = self.channel_user.get()
        Config.channel_name = self.channel_name.get()
        Config.channel_user = self.channel_user.get()
        settings = get_current_settings()
        with open('config.json', 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)

    def dial_check(self, input_region):
        screenshot = self.screen.im
        result = app_detect.detect(self.pool, screenshot, input_region)
        return result

    def intersect_area(self, a, b):
        a_xmin, a_ymin, a_xmax, a_ymax = a[0], a[1], a[2] + a[0], a[3] + a[1]
        b_xmin, b_ymin, b_xmax, b_ymax = b[0], b[1], b[2] + b[0], b[3] + b[1]
        dx = min(a_xmax, b_xmax) - max(a_xmin, b_xmin)
        dy = min(a_ymax, b_ymax) - max(a_ymin, b_ymin)
        if (dx >= 0) and (dy >= 0):
            return dx * dy
        return 0

    def intersect_xy(self, a, b):
        a_xmin, a_ymin, a_xmax, a_ymax = a[0], a[1], a[2] + a[0], a[3] + a[1]
        b_xmin, b_ymin, b_xmax, b_ymax = b[0], b[1], b[2] + b[0], b[3] + b[1]
        xl, xr = max(a_xmin, b_xmin), min(a_xmax, b_xmax)
        yl, yr = max(a_ymin, b_ymin), min(a_ymax, b_ymax)
        return xl, yl, xr, yr

    def check_area_duplicate(self):
        a = self.config.app_region[-1]
        a_center_x, a_center_y = a[0] + a[2] / 2, a[1] + a[3] / 2
        for i in range(len(self.config.app_region) - 1):
            b = self.config.app_region[i]
            xl, yl, xr, yr = self.intersect_xy(a, b)
            b_center_x, b_center_y = b[0] + b[2] / 2, b[1] + b[3] / 2
            if xl < a_center_x < xr and yl < a_center_y < yr:
                return True
            if xl < b_center_x < xr and yl < b_center_y < yr:
                return True
        return False

    def is_web_whatsapp(self, app_region):
        screenshot = self.screen.im
        rgb1 = screenshot.getpixel((app_region[0] + 50, app_region[1] + 10))
        rgb2 = screenshot.getpixel((app_region[0] + 60, app_region[1] + 10))
        rgb3 = screenshot.getpixel((app_region[0] + 80, app_region[1] + 10))
        if rgb1 == (0, 191, 165) and rgb2 == (0, 191, 165) and rgb3 == (0, 191, 165):
            return False
        return True

    def save(self):
        dial_check_result = self.dial_check(self.config.input_region[-1])
        msg = 'continue'
        if dial_check_result == -1:
            self.master.call("wm", "attributes", ".", "-topmost", "false")
            dial_check_messagebox = DialCheckMessagebox(self.master)
            self.master.wait_window(dial_check_messagebox)
            self.master.call("wm", "attributes", ".", "-topmost", "true")
            msg = dial_check_messagebox.message

        self.btn_app_pos['state'] = 'normal'
        self.prompt_index = 0
        self.button_label['fg'] = 'red'
        self.button_label['text'] = self.prompt_msg[self.prompt_index]
        if self.screen_running:
            self.screen.rect_num = 0

        if len(self.config.app_type) == 0:
            Config.selected_app_type = []

        if msg == 'continue' and not self.check_area_duplicate():
            if len(self.config.app_region) > 0 and len(self.config.input_region) > 0:
                self.btn_start['state'] = 'normal'
            if dial_check_result == -1:
                self.config.app_type.append(0)
            else:
                self.config.app_type.append(dial_check_result)
            if dial_check_result == Config.app_type_whatsapp and self.is_web_whatsapp(self.config.app_region[-1]):
                y = self.config.app_region[-1][1] - Config.whatsapp_title_height
                height = self.config.app_region[-1][3] + Config.whatsapp_title_height
                app_region = self.config.app_region[-1][0], y, self.config.app_region[-1][2], height
                self.config.app_region.pop()
                self.config.app_region.append(app_region)
            Config.selected_app_type.append(self.config.app_type_dict[self.config.app_type[-1]])
            self.save_btn['state'] = 'normal'
            self.save_btn['image'] = self.reset_icon
            self.save_btn['command'] = self.reset
            self.save_sample_image(self.config.app_type[-1])
            RpaProcess.app_status.append(1)
            self.screen.destroy()
            self.screen_running = False
            self.screen = None
        else:
            self.screen.clear_last()
            self.btn_app_pos_action(2)

    def save_sample_image(self, app_type):
        screenshot = self.screen.im
        search_x_offset, search_y_offset = Config.search_point_offset[app_type]
        if app_type == Config.app_type_whatsapp:
            search_input_x = self.config.contact_region[-1][0] + self.config.contact_region[-1][2] - search_x_offset
        else:
            search_input_x = self.config.contact_region[-1][0] + search_x_offset
        search_input_y = self.config.contact_region[-1][1] + search_y_offset
        search_pos_region = (search_input_x, search_input_y, Config.sample_icon_size, Config.sample_icon_size)
        self.config.search_pos.append(search_pos_region)
        right_down_x, right_down_y = search_input_x + Config.sample_icon_size, search_input_y + Config.sample_icon_size
        search_sample_image = screenshot.crop((search_input_x, search_input_y, right_down_x, right_down_y))
        self.config.search_sample.append(search_sample_image)
        if app_type in (Config.app_type_qq, Config.app_type_qq_full):
            Config.dymatic_binarize_threshold = np.average(np.asarray(search_sample_image))
            bin_search_sample_image = image_binarize(search_sample_image, Config.dymatic_binarize_threshold)
        else:
            bin_search_sample_image = image_binarize(search_sample_image, Config.image_binarize_threshold)
        self.config.bin_search_sample.append(bin_search_sample_image)

        input_region = self.config.input_region[-1]

        if app_type == Config.app_type_line:
            search_input_x = input_region[0] + 20
            search_input_y = input_region[1] + 90
        else:
            search_input_x = input_region[0] + Config.input_icon_offset[0]
            search_input_y = input_region[1] + Config.input_icon_offset[1]
        icon_pos_region = (search_input_x, search_input_y, Config.sample_icon_size, Config.sample_icon_size)
        self.config.icon_pos.append(icon_pos_region)
        right_down_x, right_down_y = search_input_x + Config.sample_icon_size, search_input_y + Config.sample_icon_size
        icon_sample_image = screenshot.crop((search_input_x, search_input_y, right_down_x, right_down_y))
        self.config.icon_sample.append(icon_sample_image)
        bin_icon_sample = image_binarize(icon_sample_image, Config.image_binarize_threshold)
        self.config.bin_icon_sample.append(bin_icon_sample)

        input_region = self.config.input_region[-1]
        search_input_x = input_region[0] + input_region[2] - Config.send_button_offset[app_type][0]
        search_input_y = input_region[1] + input_region[3] - Config.send_button_offset[app_type][1]
        send_btn_region = (search_input_x, search_input_y, Config.sample_icon_size, Config.sample_icon_size)
        self.config.send_btn_pos.append(send_btn_region)
        right_down_x, right_down_y = search_input_x + Config.sample_icon_size, search_input_y + Config.sample_icon_size
        send_btn_sample_image = screenshot.crop((search_input_x, search_input_y, right_down_x, right_down_y))
        self.config.send_btn_sample.append(send_btn_sample_image)
        if app_type in (Config.app_type_qq, Config.app_type_qq_full):
            bin_send_btn_sample = image_binarize(send_btn_sample_image, Config.dymatic_binarize_threshold)
        else:
            bin_send_btn_sample = image_binarize(send_btn_sample_image, Config.image_binarize_threshold)
        self.config.bin_send_btn_sample.append(bin_send_btn_sample)

    def open_url(self, event):
        webbrowser.open('http://saas.landingbj.com?channel=' + self.config.channel_name +
                        '&user=' + self.config.channel_user, new=2)

    def on_closing(self):
        if self.screen_running:
            self.screen.destroy()
        if self.rpa is not None:
            self.rpa.abort = True
        self.master.destroy()

    def set_prompt_msg(self, prompt_index, color):
        self.prompt_index = prompt_index
        self.button_label['fg'] = color
        self.button_label['text'] = self.prompt_msg[self.prompt_index]

    def move_app(self):
        resolution = pg.size()
        monitor_region = autogui.get_monitor_region()
        left_x, right_x, left_y, right_y = monitor_region[0] + monitor_region[2], monitor_region[0], 0, 0
        if sum(RpaProcess.app_status) == 0:
            return
        for i in range(len(self.config.app_region)):
            if RpaProcess.app_status[i] == 0:
                continue
            x, y, width, height = autogui.get_abs_region(self.config.app_region[i])
            xr = x + width
            if x < left_x:
                left_x, left_y = x, y + 1
                left_app = i
            if xr > right_x:
                right_x, right_y = xr, y + 1
                right_app = i

        if resolution.width - right_x >= self.init_width:
            if self.master.state() == 'iconic':
                self.master.wm_state('normal')
            self.master.geometry('%dx%d+%d+%d' % (self.init_width, self.init_height, right_x, right_y))
            Config.attach_app_index = right_app
        elif left_x >= self.init_width:
            if self.master.state() == 'iconic':
                self.master.wm_state('normal')
            self.master.geometry('%dx%d+%d+%d' % (self.init_width, self.init_height, left_x - self.init_width, left_y))
            Config.attach_app_index = left_app
        else:
            self.master.wm_state('iconic')

    def load_contact_images(self):
        if Config.scale_ratio == 1.25:
            Config.scale_ratio_index = 1
        elif Config.scale_ratio == 1.5:
            Config.scale_ratio_index = 2
        else:
            Config.scale_ratio_index = 0

        Config.yes_contact_images = []
        Config.no_contact_images = []
        Config.ding6_prompt_images = []
        Config.yes_contact_bin_images = []
        Config.no_contact_bin_images = []
        Config.ding6_prompt_bin_images = []

        yes_contact_icons = Config.yes_contact_icons[Config.scale_ratio_index]
        for i in range(len(yes_contact_icons)):
            image_path = yes_contact_icons[i]
            if image_path == '':
                Config.yes_contact_images.append(None)
                Config.yes_contact_bin_images.append(None)
            else:
                yes_contact_icon = Image.open(image_path).convert('L')
                bin_yes_contact_icon = image_binarize(yes_contact_icon, Config.image_binarize_threshold)
                Config.yes_contact_images.append(yes_contact_icon)
                Config.yes_contact_bin_images.append(bin_yes_contact_icon)

        yes_group_icons = Config.yes_group_icons[Config.scale_ratio_index]
        for i in range(len(yes_group_icons)):
            image_path = yes_group_icons[i]
            if image_path == '':
                Config.yes_group_images.append(None)
                Config.yes_group_bin_images.append(None)
            else:
                yes_group_icon = Image.open(image_path).convert('L')
                bin_yes_group_icon = image_binarize(yes_group_icon, Config.image_binarize_threshold)
                Config.yes_group_images.append(yes_group_icon)
                Config.yes_group_bin_images.append(bin_yes_group_icon)

        Config.yes_wechat_public_bin_images = Image.open(Config.yes_wechat_public_icon[Config.scale_ratio_index]).convert('L')

        no_contact_icons = Config.no_contact_icons[Config.scale_ratio_index]
        for i in range(len(no_contact_icons)):
            image_path = no_contact_icons[i]
            if image_path == '':
                Config.no_contact_images.append(None)
                Config.no_contact_bin_images.append(None)
            else:
                no_contact_icon = Image.open(image_path).convert('L')
                if i == Config.app_type_weibo:
                    binarize_threshold = 100
                else:
                    binarize_threshold = Config.image_binarize_threshold
                bin_no_contact_icon = image_binarize(no_contact_icon, binarize_threshold)
                Config.no_contact_images.append(no_contact_icon)
                Config.no_contact_bin_images.append(bin_no_contact_icon)

        for image_path in Config.ding6_contact_prompt:
            contact_icon = Image.open(image_path).convert('L')
            bin_contact_icon = image_binarize(contact_icon, Config.image_binarize_threshold)
            Config.ding6_prompt_images.append(contact_icon)
            Config.ding6_prompt_bin_images.append(bin_contact_icon)

    def rpa_start(self):
        if len(self.config.app_region) == 0 or len(self.config.input_region) == 0:
            messagebox.showwarning(title='警告', message='请先标定软件和输入框的位置！')
            return
        if self.screen_running:
            self.screen.destroy()
            self.screen_running = False
            self.screen = None
        self.btn_start['image'] = self.stop_icon
        self.btn_start['command'] = self.rpa_stop
        self.btn_app_pos['state'] = 'disabled'
        self.save_btn['state'] = 'disabled'
        self.move_app()
        self.load_contact_images()
        RpaProcess.last_app_status = [i for i in RpaProcess.app_status]
        config_list = self.copy_config()
        self.rpa_list = []
        self.close_rpa_setting()

        for i in range(len(config_list)):
            rpa = RpaProcess(config_list[i], self, i)
            rpa.start()
            self.rpa_list.append(rpa)
        size = len(config_list)
        Config.topmost_matrix = [[0] * size for i in range(size)]
        self.init_topmost_matrix()
        self.set_prompt_msg(4, 'black')

    def init_topmost_matrix(self):
        size = len(Config.topmost_matrix)
        for i in range(size):
            for j in range(size):
                if i == j:
                    continue
                if self.intersect_area(self.config.app_region[i], self.config.app_region[j]) > 0:
                    Config.topmost_matrix[i][j] = 1

        for i in range(size):
            if sum(Config.topmost_matrix[i]) == 0:
                Config.topmost_matrix[i][i] = -1

    def copy_config(self):
        config_list = []
        for i in range(len(self.config.input_region)):
            conf = Config()
            conf.input_region.append(self.config.input_region[i])
            conf.app_region.append(self.config.app_region[i])
            conf.app_type.append(self.config.app_type[i])
            conf.period = self.config.period
            conf.channel_name = self.config.channel_name
            conf.channel_user = self.config.channel_user
            conf.search_pos.append(self.config.search_pos[i])
            conf.icon_pos.append(self.config.icon_pos[i])
            conf.send_btn_pos.append(self.config.send_btn_pos[i])
            conf.search_sample.append(self.config.search_sample[i])
            conf.icon_sample.append(self.config.icon_sample[i])
            conf.send_btn_sample.append(self.config.send_btn_sample[i])
            conf.bin_search_sample.append(self.config.bin_search_sample[i])
            conf.bin_icon_sample.append(self.config.bin_icon_sample[i])
            conf.bin_send_btn_sample.append(self.config.bin_send_btn_sample[i])
            config_list.append(conf)
        return config_list

    def rpa_stop(self):
        for rpa in self.rpa_list:
            rpa.abort = True
        self.btn_start['command'] = self.rpa_start
        self.btn_start['image'] = self.start_icon
        self.btn_app_pos['state'] = 'normal'
        self.save_btn['state'] = 'normal'
        self.save_btn['command'] = self.reset
        self.set_prompt_msg(0, 'red')

    def reset(self):
        self.config.app_region.clear()
        self.config.input_region.clear()
        self.config.app_type.clear()
        self.config.search_pos.clear()
        self.config.icon_pos.clear()
        self.config.send_btn_pos.clear()
        self.config.search_sample.clear()
        self.config.icon_sample.clear()
        self.config.send_btn_sample.clear()
        self.config.bin_search_sample.clear()
        self.config.bin_icon_sample.clear()
        self.config.bin_send_btn_sample.clear()
        self.config.selected_app_type.clear()
        RpaProcess.app_status.clear()
        self.save_btn['image'] = self.save_icon
        self.save_btn['command'] = self.save
        self.save_btn['state'] = 'disabled'
        self.btn_start['state'] = 'disabled'
        self.btn_app_pos['state'] = 'normal'
        self.set_prompt_msg(0, 'red')
        if self.screen_running:
            self.screen.destroy()
            self.screen_running = False
            self.screen = None

    def btn_app_pos_action(self, flag):
        self.close_rpa_setting()
        if os.path.isfile(Config.screenshot):
            os.remove(Config.screenshot)
        if flag == 1:
            self.save_btn['state'] = 'disabled'
            self.save_btn['image'] = self.save_icon
            self.save_btn['command'] = self.save
        elif flag == 2:
            self.save_btn['state'] = 'normal'
            self.save_btn['image'] = self.reset_icon
            self.save_btn['command'] = self.reset
        self.btn_app_pos['state'] = 'disabled'
        self.btn_start['state'] = 'disabled'
        self.prompt_index = 1
        self.button_label['fg'] = 'red'
        self.button_label['text'] = self.prompt_msg[self.prompt_index]
        if self.screen is None:
            self.master.attributes('-alpha', 0)
            pos = self.master.geometry().split('+')
            autogui.current_monitor = autogui.get_monitor_index(int(pos[1]), int(pos[2]))
            self.screen = Screen(self, autogui.screenshot())
            self.master.attributes('-alpha', 255)
        self.screen_running = True
        self.screen.mainloop()