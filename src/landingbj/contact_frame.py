# cython: language_level=3
import csv
from pathlib import Path
from tkinter import Frame, TOP, Label, NW, Button, StringVar, Entry, LEFT, RIGHT, \
    filedialog, Tk, Canvas, END, W, Text, FLAT, DISABLED, NORMAL
from tkinter.ttk import Combobox

import numpy as np
import pyautogui
from PIL import ImageTk, ImageFilter, Image
from ai.image import find_edge

from landingbj import qa
from landingbj.agent_config import AgentConfig
from landingbj.config import Config
from landingbj.qa import get_rpa_contact, get_app_type_list, add_app_contact, update_app_contact, delete_app_contact, \
    get_guide_list, add_rpa_guide
from landingbj.social_rpa import SocialConfig, SocialProcess, url_cache


class ContactFrame(Frame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.parent = parent
        self.main = main

        self.app_type = get_app_type_list()

        self.contact_frame = Frame(self.parent, borderwidth=0)
        self.contact_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 10), fill='x')

        self.contact_title_frame = Frame(self.contact_frame, borderwidth=0, bg='white')
        self.contact_title_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(10, 0), fill='x')

        self.contact_icon = ImageTk.PhotoImage(Image.open(Config.add_contact_icon).resize((22, 22), Image.ANTIALIAS))
        self.expand_icon = ImageTk.PhotoImage(Image.open(Config.expand_icon).resize((22, 22), Image.ANTIALIAS))
        self.shrink_icon = ImageTk.PhotoImage(Image.open(Config.shrink_icon).resize((22, 22), Image.ANTIALIAS))

        contact_icon_label = Label(self.contact_title_frame, borderwidth=0, image=self.contact_icon, bg='white')
        contact_icon_label.pack(side=LEFT, anchor=NW, pady=5, padx=(30, 0), fill='y')

        contact_label = Label(self.contact_title_frame, width=10, borderwidth=0, text='联系人', bg='white', anchor='w')
        contact_label.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='y')

        self.contact_expand_btn = Button(self.contact_title_frame, image=self.shrink_icon, borderwidth=0, bg='white')
        self.contact_expand_btn.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW)

        self.contact_main_frame = Frame(self.contact_frame, borderwidth=0)
        self.hide_contact_main()

        self.app_type_frame = AppTypeFrame(self.contact_main_frame, bg='white')
        self.app_type_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')

        self.app_type_frame.on_change = self.reload_contact

        self.add_contact_frame = AddContactFrame(self.contact_main_frame, self, bg='white')
        self.add_contact_frame.update_contact = self.reload_contact
        self.add_contact_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')

        self.contact_list_frame = None
        self.reload_contact(self.app_type_frame.app_type_comvalue.get())

        role = qa.get_user_role({'username': Config.channel_user})
        self.rpa_frame = Frame(self.parent, borderwidth=0)
        if role > 1:
            self.rpa_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 10), fill='x')

        self.rpa_title_frame = Frame(self.rpa_frame, borderwidth=0, bg='white')
        self.rpa_title_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        self.contact_advance_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_advance_icon).resize((20, 20), Image.ANTIALIAS))

        contact_advance_icon_label = Label(self.rpa_title_frame, borderwidth=0, image=self.contact_advance_icon,
                                           bg='white')
        contact_advance_icon_label.pack(side=LEFT, anchor=NW, pady=5, padx=(30, 0), fill='y')

        contact_advance_label = Label(self.rpa_title_frame, width=10, borderwidth=0, text='高级设置', bg='white',
                                      anchor='w')
        contact_advance_label.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='y')

        self.contact_advance_expand_btn = Button(self.rpa_title_frame, image=self.shrink_icon, borderwidth=0,
                                                 bg='white')
        self.contact_advance_expand_btn.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW)

        self.rpa_main_frame = Frame(self.rpa_frame, borderwidth=0, bg='white')
        self.show_rpa_main()

        self.advance_app_type_frame = AppTypeFrame(self.rpa_main_frame, app_type={'抖音': '', '快手': '', 'QQ': ''},
                                                   bg='white')
        self.advance_app_type_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')

        self.advance_app_type_frame.on_change = self.app_type_on_change

        self.guide_data = get_guide_list()

        self.qq_frame = QqFrame(self.rpa_main_frame, self.main, self.guide_data)
        self.tiktok_frame = TiktokFrame(self.rpa_main_frame, self.main, self.guide_data)
        self.tiktok_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')
        self.kuaishou_frame = KuaishouFrame(self.rpa_main_frame, self.main, self.guide_data)

    def show_contact_main(self):
        self.contact_main_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(1, 0), fill='x')
        self.contact_expand_btn['command'] = self.hide_contact_main
        self.contact_expand_btn['image'] = self.shrink_icon

    def hide_contact_main(self):
        self.contact_main_frame.pack_forget()
        self.contact_expand_btn['command'] = self.show_contact_main
        self.contact_expand_btn['image'] = self.expand_icon

    def show_rpa_main(self):
        self.rpa_main_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(1, 0), fill='x')
        self.contact_advance_expand_btn['command'] = self.hide_rpa_main
        self.contact_advance_expand_btn['image'] = self.shrink_icon

    def hide_rpa_main(self):
        self.rpa_main_frame.pack_forget()
        self.contact_advance_expand_btn['command'] = self.show_rpa_main
        self.contact_advance_expand_btn['image'] = self.expand_icon

    def reload_contact(self, choice):
        if self.contact_list_frame is not None:
            self.contact_list_frame.destroy()
        self.contact_list_frame = Frame(self.contact_main_frame, borderwidth=0)
        contact_name_list = get_rpa_contact(self.app_type[choice])['data']
        for contact_info in contact_name_list:
            ContactItemFrame(self.contact_list_frame, contact=contact_info, bg='white'). \
                pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.contact_list_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')

    def app_type_on_change(self, choice):
        if choice == '抖音':
            self.qq_frame.pack_forget()
            self.kuaishou_frame.pack_forget()
            self.tiktok_frame.pack(side=TOP, anchor=NW, padx=(0, 0), fill='x')
        elif choice == 'QQ':
            self.tiktok_frame.pack_forget()
            self.kuaishou_frame.pack_forget()
            self.qq_frame.pack(side=TOP, anchor=NW, padx=(0, 0), fill='x')
        elif choice == '快手':
            self.qq_frame.pack_forget()
            self.tiktok_frame.pack_forget()
            self.kuaishou_frame.pack(side=TOP, anchor=NW, padx=(0, 0), fill='x')


SEARCH_ADD_CONTACT = '搜索并添加好友'
UPLOAD_ADD_CONTACT = '上传通讯录并添加好友'


class AddContactFrame(Frame):
    def __init__(self, master=None, parent=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.parent = parent
        self.app_type = get_app_type_list()
        new_contact_label = Label(self, width=10, text='用户或群', bg='white', anchor='w')
        new_contact_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        self.new_contact_entry = Entry(self, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.new_contact_entry.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(5, 5), fill='y')

        self.add_btn_image = ImageTk.PhotoImage(
            Image.open(Config.add_btn).resize((50, 23), Image.ANTIALIAS))
        new_contact_btn = Button(self, image=self.add_btn_image, bg='white', borderwidth=0,
                                 command=self.add_new_contact)
        new_contact_btn.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='y')

        self.update_contact = lambda contacts, current_app: None

    def add_new_contact(self):
        current_app = self.parent.app_type_frame.app_type_comvalue.get()
        if len(self.new_contact_entry.get().strip()) == 0:
            return
        data = {
            "appId": self.app_type[current_app],
            "contactName": self.new_contact_entry.get()
        }
        add_app_contact(data)
        self.update_contact(current_app)
        self.new_contact_entry.delete(0, END)


class AppTypeFrame(Frame):
    def __init__(self, master=None, app_type=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)

        if app_type is None:
            self.app_type = get_app_type_list()
        else:
            self.app_type = app_type

        self.app_type_label = Label(self, width=10, text='软件类型', bg='white', anchor='w')
        self.app_type_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(10, 5), fill='y')

        self.app_type_comvalue = StringVar()
        self.app_type_comboxlist = Combobox(self, state="readonly",
                                            textvariable=self.app_type_comvalue)
        self.app_type_comboxlist["values"] = tuple(self.app_type.keys())
        self.app_type_comboxlist.current(0)

        self.on_change = lambda choice: None
        self.app_type_comboxlist.bind("<<ComboboxSelected>>", self.app_on_change)
        self.app_type_comboxlist.unbind_class("TCombobox", "<MouseWheel>")
        self.app_type_comboxlist.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

    def app_on_change(self, event):
        choice = event.widget.get()
        self.on_change(choice)


class ContactItemFrame(Frame):
    def __init__(self, master=None, contact={}, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.contact = contact
        self.delete_btn_icon = ImageTk.PhotoImage(
            Image.open(Config.delete_contact_icon).resize((27, 27), Image.ANTIALIAS))
        self.save_btn_icon = ImageTk.PhotoImage(Image.open(Config.save_contact_icon).resize((27, 27), Image.ANTIALIAS))
        self.edit_btn_icon = ImageTk.PhotoImage(
            Image.open(Config.update_contact_icon).resize((27, 27), Image.ANTIALIAS))

        self.contact_text = Text(self, bg='white', width=30, height=1, bd=0, spacing1=7, spacing3=7, relief=FLAT)
        self.contact_text.config(wrap='none')
        self.contact_text.insert(END, self.contact['contactName'].strip())
        if self.contact_text.get('end-1c', END) == '\n':
            self.contact_text.delete('end-1c', END)
        self.contact_text.config(state=DISABLED)
        self.contact_text.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5))

        self.save_btn = Button(self, bg='white', image=self.edit_btn_icon, borderwidth=0,
                               command=self.edit)
        self.save_btn.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='y')

        self.delete_btn = Button(self, bg='white', image=self.delete_btn_icon, borderwidth=0,
                                 command=self.delete)
        self.delete_btn.pack(side=RIGHT, anchor=NW, padx=(0, 0), pady=(5, 5), fill='y')

    def delete(self):
        data = {
            "id": self.contact['id'],
            "channelId": self.contact['channelId'],
            "appId": self.contact['appId'],
            "contactName": self.contact['contactName'],
        }
        result = delete_app_contact(data)
        if result['status'] == 'success':
            self.pack_forget()

    def edit(self):
        self.contact_text.config(state=NORMAL)
        self.contact_text.focus()
        self.save_btn['image'] = self.save_btn_icon
        self.save_btn['command'] = self.save

    def save(self):
        data = {
            "id": self.contact['id'],
            "channelId": self.contact['channelId'],
            "appId": self.contact['appId'],
            "contactName": self.contact_text.get("1.0", END).strip(),
        }
        result = update_app_contact(data)
        if result['status'] == 'success':
            self.save_btn['image'] = self.edit_btn_icon
            self.save_btn['command'] = self.edit
            self.contact_text.config(state=DISABLED)
        else:
            self.contact_text.focus()


class TiktokFrame(Frame):
    def __init__(self, master=None, main=None, data=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.main = main

        self.frame1 = Frame(self, bg='white')
        self.frame1.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')

        self.search_label = Label(self.frame1, width=10, text='搜索关键词', bg='white', anchor='w')
        self.search_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')
        self.search_entry = Entry(self.frame1, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.search_entry.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.frame2 = Frame(self, bg='white')
        self.frame2.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.new_reply_keyword_label = Label(self.frame2, width=10, text='回复关键词', bg='white', anchor='w')
        self.new_reply_keyword_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')
        self.new_reply_keyword_entry = Entry(self.frame2, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.new_reply_keyword_entry.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.contact_start_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_start_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_stop_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_stop_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_pos_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_pos_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_reset_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_reset_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_commit_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_commit_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_save_icon = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))

        self.frame4 = Frame(self, bg='white')
        self.frame4.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.reset_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_reset_icon,
                                command=lambda: self.reset())
        # self.reset_btn.pack(side=LEFT, padx=(30, 0), pady=(5, 5), anchor=NW)
        self.pos_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_pos_icon,
                              command=lambda: self.get_pos())
        # self.pos_btn.pack(side=LEFT, padx=(23, 0), pady=(5, 5), anchor=NW, expand=True)

        self.save_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_commit_icon,
                               command=lambda: self.commit())
        self.save_btn.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW)

        self.start_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_start_icon,
                                command=lambda: self.start())
        self.start_btn.pack(side=RIGHT, padx=(0, 23), pady=(5, 5), anchor=NW)

        self.screen_running = False
        self.screen = None
        self.tiktok_contact_region = None
        if data is not None and ('抖音', 1) in data:
            n = data[('抖音', 1)]
            self.search_entry.insert(0, n['searchStr'])
            self.new_reply_keyword_entry.insert(0, n['replyKeyword'])

    def get_pos(self):
        self.main.attributes('-alpha', 0)
        self.screen = Screen(pyautogui.screenshot(), self.screen_on_release)
        self.main.attributes('-alpha', 255)
        self.screen_running = True

    def screen_on_release(self):
        self.pos_btn['image'] = self.contact_save_icon
        self.pos_btn['command'] = self.save

    def reset(self):
        if self.screen_running:
            self.screen.destroy()
            self.screen_running = False
            # self.screen = None
            self.pos_btn['image'] = self.contact_pos_icon
            self.pos_btn['command'] = self.get_pos
            SocialConfig.tiktok_contact_region = None

    def save(self):
        if self.screen_running:
            self.tiktok_contact_region = self.screen.get_region()
            self.screen.destroy()
            self.screen_running = False
            self.pos_btn['image'] = self.contact_pos_icon
            self.pos_btn['command'] = self.get_pos
            # SocialConfig.set_tiktok_contact_pos(self.tiktok_contact_region)

    def start(self):
        # if SocialConfig.tiktok_contact_region is None:
        #     return
        search_keyword = self.search_entry.get()
        if len(search_keyword.strip()) == 0:
            return
        self.main.wm_state('iconic')
        self.start_btn['image'] = self.contact_stop_icon
        self.start_btn['command'] = self.stop
        SocialConfig.abort = False
        AgentConfig.browser_tab = {Config.app_type_tiktok: [1], Config.app_type_kuaishou: [1]}
        reply_keyword = self.new_reply_keyword_entry.get()
        rpa_guide_data = {'searchStr': search_keyword, 'replyKeyword': reply_keyword}
        SocialProcess(rpa_guide_data, Config.app_type_tiktok).start()

    def stop(self):
        self.start_btn['image'] = self.contact_start_icon
        self.start_btn['command'] = self.start
        SocialConfig.abort = True
        url_cache.clear()

    def commit(self):
        search_keyword = self.search_entry.get().strip()
        reply_keyword = self.new_reply_keyword_entry.get().strip()
        data = {
            "id": -1,
            "appId": 10,
            "searchStr": search_keyword,
            'replyKeyword': reply_keyword,
            "type": 1
        }
        if len(search_keyword) == 0 or len(reply_keyword) == 0:
            return
        add_rpa_guide(data)


class KuaishouFrame(Frame):
    def __init__(self, master=None, main=None, data=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.main = main

        self.frame1 = Frame(self, bg='white')
        self.frame1.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')

        self.search_label = Label(self.frame1, width=10, text='搜索关键词', bg='white', anchor='w')
        self.search_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')
        self.search_entry = Entry(self.frame1, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.search_entry.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.frame2 = Frame(self, bg='white')
        self.frame2.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.new_reply_keyword_label = Label(self.frame2, width=10, text='回复关键词', bg='white', anchor='w')
        self.new_reply_keyword_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')
        self.new_reply_keyword_entry = Entry(self.frame2, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.new_reply_keyword_entry.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.contact_start_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_start_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_stop_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_stop_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_pos_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_pos_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_reset_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_reset_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_commit_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_commit_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_save_icon = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))

        self.frame4 = Frame(self, bg='white')
        self.frame4.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.reset_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_reset_icon,
                                command=lambda: self.reset())
        # self.reset_btn.pack(side=LEFT, padx=(30, 0), pady=(5, 5), anchor=NW)
        self.pos_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_pos_icon,
                              command=lambda: self.get_pos())
        # self.pos_btn.pack(side=LEFT, padx=(23, 0), pady=(5, 5), anchor=NW, expand=True)
        self.save_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_commit_icon,
                               command=lambda: self.commit())
        self.save_btn.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW)

        self.start_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_start_icon,
                                command=lambda: self.start())
        self.start_btn.pack(side=RIGHT, padx=(0, 23), pady=(5, 5), anchor=NW)

        self.screen_running = False
        self.screen = None
        self.tiktok_contact_region = None
        if data is not None and ('快手', 1) in data:
            n = data[('快手', 1)]
            self.search_entry.insert(0, n['searchStr'])
            self.new_reply_keyword_entry.insert(0, n['replyKeyword'])

    def get_pos(self):
        self.main.attributes('-alpha', 0)
        self.screen = Screen(pyautogui.screenshot(), self.screen_on_release)
        self.main.attributes('-alpha', 255)
        self.screen_running = True

    def screen_on_release(self):
        self.pos_btn['image'] = self.contact_save_icon
        self.pos_btn['command'] = self.save

    def reset(self):
        if self.screen_running:
            self.screen.destroy()
            self.screen_running = False
            # self.screen = None
            self.pos_btn['image'] = self.contact_pos_icon
            self.pos_btn['command'] = self.get_pos
            SocialConfig.tiktok_contact_region = None

    def save(self):
        if self.screen_running:
            self.tiktok_contact_region = self.screen.get_region()
            self.screen.destroy()
            self.screen_running = False
            self.pos_btn['image'] = self.contact_pos_icon
            self.pos_btn['command'] = self.get_pos
            SocialConfig.set_tiktok_contact_pos(self.tiktok_contact_region)

    def start(self):
        # if SocialConfig.tiktok_contact_region is None:
        #     return
        search_keyword = self.search_entry.get()
        if len(search_keyword.strip()) == 0:
            return
        self.main.wm_state('iconic')
        self.start_btn['image'] = self.contact_stop_icon
        self.start_btn['command'] = self.stop
        SocialConfig.abort = False
        AgentConfig.browser_tab = {Config.app_type_tiktok: [1], Config.app_type_kuaishou: [1]}
        reply_keyword = self.new_reply_keyword_entry.get()
        rpa_guide_data = {'searchStr': search_keyword, 'replyKeyword': reply_keyword}
        SocialProcess(rpa_guide_data, Config.app_type_kuaishou).start()

    def stop(self):
        self.start_btn['image'] = self.contact_start_icon
        self.start_btn['command'] = self.start
        SocialConfig.abort = True
        url_cache.clear()

    def commit(self):
        search_keyword = self.search_entry.get().strip()
        reply_keyword = self.new_reply_keyword_entry.get().strip()
        data = {
            "id": -1,
            "appId": 11,
            "searchStr": search_keyword,
            'replyKeyword': reply_keyword,
            "type": 1
        }
        if len(search_keyword) == 0 or len(reply_keyword) == 0:
            return
        add_rpa_guide(data)


class QqFrame(Frame):
    def __init__(self, master=None, main=None, data=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self.main = main
        self.frame1 = Frame(self, bg='white')
        self.frame1.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')

        self.func_type_label = Label(self.frame1, width=10, text='选择功能', bg='white', anchor='w')
        self.func_type_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(10, 5), fill='y')
        self.method_comvalue = StringVar()
        self.method_comboxlist = Combobox(self.frame1, state="readonly", textvariable=self.method_comvalue)
        self.method_comboxlist["values"] = (SEARCH_ADD_CONTACT)
        self.method_comboxlist.current(0)
        self.method_comboxlist.bind("<<ComboboxSelected>>", self.method_on_change)
        self.method_comboxlist.unbind_class("TCombobox", "<MouseWheel>")
        self.method_comboxlist.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.func_frame = Frame(self, bg='white')
        self.func_frame.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.frame2 = Frame(self.func_frame, bg='white')
        self.frame2.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')
        self.search_label = Label(self.frame2, width=10, text='关键词', bg='white', anchor='w')
        self.search_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')
        self.search_entry = Entry(self.frame2, width=18, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.search_entry.pack(side=RIGHT, anchor=NW, padx=(0, 30), pady=(5, 5), fill='both', expand=True)

        self.frame3 = Frame(self.func_frame, bg='white')
        self.label_file_explorer = Label(self.frame3, width=10, anchor=W, text="未选择文件", bg='white')
        self.label_file_explorer.pack(side=LEFT, padx=(30, 0), pady=(5, 5), anchor=NW, fill='y')
        self.button_explore = Button(self.frame3, text="选择文件", bg='white', borderwidth=1, command=self.browseFiles)
        self.button_explore.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW, fill='y')

        self.contact_start_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_start_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_stop_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_stop_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_pos_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_pos_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_reset_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_reset_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_commit_icon = ImageTk.PhotoImage(
            Image.open(Config.contact_commit_icon).resize((50, 23), Image.ANTIALIAS))
        self.contact_save_icon = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))

        self.frame4 = Frame(self, bg='white')
        self.frame4.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(1, 0), fill='x')
        self.reset_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_reset_icon,
                                command=lambda: self.reset())
        self.reset_btn.pack(side=LEFT, padx=(30, 0), pady=(5, 5), anchor=NW)
        self.pos_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_pos_icon,
                              command=lambda: self.get_pos())
        self.pos_btn.pack(side=LEFT, padx=(23, 0), pady=(5, 5), anchor=NW, expand=True)
        self.save_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_commit_icon,
                               command=lambda: self.commit())
        self.save_btn.pack(side=RIGHT, padx=(0, 30), pady=(5, 5), anchor=NW)
        self.start_btn = Button(self.frame4, bg='white', borderwidth=0, image=self.contact_start_icon,
                                command=lambda: self.start())
        self.start_btn.pack(side=LEFT, padx=(0, 23), pady=(5, 5), anchor=NW)

        self.screen_running = False
        self.screen = None

        self.qq_contact_region = None
        self.csv_filepath = None
        if data is not None and ('QQ', 1) in data:
            n = data[('QQ', 1)]
            self.search_entry.insert(0, n['searchStr'])
        if data is not None and ('QQ', 2) in data:
            n = data[('QQ', 2)]
            self.label_file_explorer.configure(text=n['fileName'])

    def method_on_change(self, event):
        choice = event.widget.get()
        if choice == SEARCH_ADD_CONTACT:
            self.frame3.pack_forget()
            self.frame2.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')
        elif choice == UPLOAD_ADD_CONTACT:
            self.frame2.pack_forget()
            self.frame3.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')

    def browseFiles(self):
        self.csv_filepath = filedialog.askopenfilename(initialdir="/", title="选择文件",
                                                       filetypes=(("CSV文件", "*.csv*"), ("all files", "*.*")))
        filename = Path(self.csv_filepath).name
        if len(filename) > 0:
            self.label_file_explorer.configure(text=filename)

    def get_pos(self):
        self.main.attributes('-alpha', 0)
        self.screen = Screen(pyautogui.screenshot(), self.screen_on_release)
        self.main.attributes('-alpha', 255)
        self.screen_running = True

    def screen_on_release(self):
        self.pos_btn['image'] = self.contact_save_icon
        self.pos_btn['command'] = self.save

    def reset(self):
        if self.screen_running:
            self.screen.destroy()
            self.screen_running = False
            self.screen = None
            self.pos_btn['image'] = self.contact_pos_icon
            self.qq_contact_region = None

    def save(self):
        if self.screen_running:
            self.qq_contact_region = self.screen.get_region()
            self.screen.destroy()
            self.screen_running = False
            self.pos_btn['image'] = self.contact_pos_icon
            self.pos_btn['command'] = self.get_pos
            SocialConfig.set_qq_contact_pos(self.qq_contact_region)

    def start(self):
        if SocialConfig.qq_contact_region is None:
            return
        SocialConfig.abort = False
        choice = self.method_comvalue.get()
        if choice == SEARCH_ADD_CONTACT:
            search_keyword = self.search_entry.get()
            if len(search_keyword.strip()) == 0:
                return
            rpa_guide_data = {'searchStr': search_keyword}
            SocialProcess(rpa_guide_data, Config.app_type_qq).start()
        elif choice == UPLOAD_ADD_CONTACT:
            keyword = []
            with open(self.csv_filepath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    keyword.append(row[1])
            # QqRpaProcess(keyword).start()
        self.main.wm_state('iconic')
        self.start_btn['image'] = self.contact_stop_icon
        self.start_btn['command'] = self.stop

    def stop(self):
        self.start_btn['image'] = self.contact_start_icon
        self.start_btn['command'] = self.start
        SocialConfig.abort = True

    def commit(self):
        search_keyword = self.search_entry.get().strip()
        data = {
            "id": -1,
            "appId": 2,
            "searchStr": search_keyword,
            "type": 1
        }
        if len(search_keyword) == 0:
            return
        add_rpa_guide(data)


class Screen(Tk):
    def __init__(self, image, on_release):
        Tk.__init__(self)
        self.on_release = on_release
        self.x = self.y = 0
        self.canvas = Canvas(self, width=512, height=512, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = self.start_y = self.curX = self.curY = 0
        self.rect_num = 0
        self.im = image
        self._draw_image()
        self.overrideredirect(True)
        self.state("zoomed")

    def _draw_image(self):
        self.tk_im = ImageTk.PhotoImage(self.im, master=self.canvas)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)
        self.edge_data = np.asarray(self.im.convert('L').filter(ImageFilter.FIND_EDGES))

    def on_button_press(self, event):
        if self.rect is not None:
            self.clear_last()
        rectangle_options = {'dash': (5, 5), 'outline_color': 'red'}
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, dash=rectangle_options['dash'],
                                                 outline=rectangle_options['outline_color'], width=2)
        self.start_x = event.x
        self.start_y = event.y

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.curX, self.curY = (event.x, event.y)
        self.start_x, self.start_y, self.curX, self.curY = find_edge(self.edge_data, self.get_region())
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)
        self.on_release()

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

    def clear_last(self):
        self.canvas.delete(self.rect)
