# cython: language_level=3
from tkinter import Frame, TOP, Label, NW, GROOVE, Button, StringVar, LEFT, RIGHT
from tkinter.ttk import Combobox, Style, Radiobutton

from PIL import ImageTk, Image

from landingbj.config import Config
from landingbj.gui_module import ContactListFrame, NewContactFrame, NewKeywordFrame, KeywordListFrame, SplitLine
from landingbj.message_box import get_login_status
from landingbj.qa import get_app_type_list, get_rpa_contact, get_keyword_list, add_repeater, update_repeater, \
    delete_repeater
from landingbj.util import get_image


class RepeaterFrame(Frame):
    def __init__(self, parent, height, width, data, setting_frame):
        super().__init__(parent)
        self.setting_frame = setting_frame
        self.parent = parent
        self.data = data

        if self.data['sendAppId'] in Config.selected_app_type or self.data['receiveAppId'] in Config.selected_app_type:
            bg_color = 'white'
        else:
            bg_color = '#dcdcdc'

        item_frame = Frame(parent, bg=bg_color, borderwidth=1)
        item_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=10, padx=5)

        frame1 = Frame(item_frame, height=height, width=width, bg=bg_color, borderwidth=1)

        self.send_app_icon = get_image(self.data['sendAppIcon'], size=(32, 32))
        send_app_icon_label = Label(frame1, bg=bg_color, image=self.send_app_icon)
        send_app_icon_label.pack(side=LEFT, anchor=NW, fill='both', expand=False, pady=(5, 10), padx=(60, 0))

        send_app_name_label = Label(frame1, text=self.data['sendAppName'], bg=bg_color)
        send_app_name_label.pack(side=LEFT, anchor=NW, fill='both', expand=False, pady=(5, 10), padx=0)

        self.arrow_icon = ImageTk.PhotoImage(Image.open(Config.arrow_icon))
        arrow_icon_label = Label(frame1, bg=bg_color, image=self.arrow_icon)
        arrow_icon_label.pack(side=LEFT, anchor=NW, fill='both', expand=True, pady=(5, 10), padx=(0, 0))

        self.receive_app_icon = get_image(self.data['receiveAppIcon'], size=(32, 32))
        receive_app_icon_label = Label(frame1, bg=bg_color, image=self.receive_app_icon)
        receive_app_icon_label.pack(side=LEFT, anchor=NW, fill='both', expand=False, pady=(5, 10), padx=(0, 0))
        receive_app_name_label = Label(frame1, text=self.data['receiveAppName'], bg=bg_color)
        receive_app_name_label.pack(side=LEFT, anchor=NW, fill='both', expand=False, pady=(5, 10),
                                    padx=(0, 60 * Config.scale_ratio))

        frame1.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=5)

        frame2 = Frame(item_frame, height=70, width=width, bg=bg_color, borderwidth=1)

        left_contact_frame = Frame(frame2, bg=bg_color, borderwidth=1)
        self.contact_icon = ImageTk.PhotoImage(Image.open(Config.contact_icon).resize((13, 13), Image.ANTIALIAS))
        contact_icon_label = Label(left_contact_frame, image=self.contact_icon, bg=bg_color)
        contact_icon_label.pack(side=LEFT, anchor=NW, fill='x', expand=True, pady=(0, 0), padx=(0, 0))

        for idx, contact in enumerate(self.data['sendContactNameList']):
            if idx > 2:
                break
            send_contact_label = Label(left_contact_frame, text=contact, anchor="w", bg=bg_color, fg='#7B7B7B')
            send_contact_label.config(font=('None', 8))
            if idx == 0:
                send_contact_label.pack(side=TOP, anchor=NW, fill='x', expand=False, pady=(0, 0), padx=(0, 0))
            else:
                send_contact_label.pack(side=TOP, anchor=NW, fill='x', expand=True, pady=(0, 0), padx=(0, 0))

        left_contact_frame.pack(side=LEFT, anchor=NW, fill='y', expand=False, pady=0, padx=(60, 0))

        right_contact_frame = Frame(frame2, bg=bg_color, borderwidth=1)
        contact_icon_label = Label(right_contact_frame, image=self.contact_icon, bg=bg_color)
        contact_icon_label.pack(side=LEFT, anchor=NW, fill='x', expand=True, pady=(0, 0), padx=(0, 0))

        for idx, contact in enumerate(self.data['receiveContactNameList']):
            if idx > 2:
                break
            receive_contact_label = Label(right_contact_frame, text=contact, anchor="w", bg=bg_color, fg='#7B7B7B',
                                          width=12)
            receive_contact_label.config(font=('None', 8))
            if idx == 0:
                receive_contact_label.pack(side=TOP, anchor=NW, fill='x', expand=False, pady=(0, 0), padx=(0, 0))
            else:
                receive_contact_label.pack(side=TOP, anchor=NW, fill='x', expand=True, pady=(0, 0), padx=(0, 0))
        right_contact_frame.pack(side=RIGHT, anchor=NW, fill='y', expand=False, pady=0,
                                 padx=(0, 28 * Config.scale_ratio))

        frame2.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=(0, 10), padx=5)

        SplitLine(item_frame)
        frame3 = Frame(item_frame, height=height, bg=bg_color, borderwidth=1)
        keywords = ' '.join(map(str, self.data['keywordList']))
        keyword_label = Label(frame3, text='关键词：' + keywords, anchor="w", bg=bg_color, fg='#7B7B7B', width=32)
        keyword_label.config(font=('None', 8))
        keyword_label.pack(side=LEFT, anchor=NW, fill='both', expand=True, pady=10, padx=5)

        self.update_btn_image = ImageTk.PhotoImage(
            Image.open(Config.update_btn).resize((50, 23), Image.ANTIALIAS))
        update_btn = Button(frame3, image=self.update_btn_image, bg=bg_color, borderwidth=0,
                            command=lambda: self.show_update_frame(data['id']))
        update_btn.pack(side=LEFT, anchor=NW, fill='both', expand=True, pady=10, padx=5)

        self.delete_btn_image = ImageTk.PhotoImage(
            Image.open(Config.delete_btn).resize((50, 23), Image.ANTIALIAS))
        delete_btn = Button(frame3, image=self.delete_btn_image, bg=bg_color, borderwidth=0,
                            command=lambda: self.delete_repeater_data(data['id']))
        delete_btn.pack(side=LEFT, anchor=NW, fill='both', expand=True, pady=10, padx=5)
        frame3.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=5)

    def show_update_frame(self, id):
        self.setting_frame.show_repeater_update_frame(id)

    def delete_repeater_data(self, data_id):
        if not get_login_status(self.setting_frame.parent):
            return

        result = delete_repeater(data_id)
        if result['status'] == 'success':
            self.setting_frame.reset_repeater_list_frame()


class RepeaterAddOrUpdateFrame(Frame):
    def __init__(self, parent, setting_frame, data=None):
        super().__init__(parent)
        self.setting_frame = setting_frame
        self.parent = parent
        self.data = data
        self.app_type = get_app_type_list()

        self.init_frame1()
        self.init_frame2()
        self.init_btn_frame()

    def init_frame1(self):
        frame1 = Frame(self.parent, bg='white', borderwidth=1)
        frame1.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(10, 0), fill='x')

        send_app_type_label = Label(frame1, width=10, text='来源于', bg='white', anchor='w')
        send_app_type_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        self.send_app_type_comvalue = StringVar()
        self.send_app_type_comboxlist = Combobox(frame1, state="readonly", textvariable=self.send_app_type_comvalue)
        self.send_app_type_comboxlist["values"] = tuple(self.app_type.keys())
        if self.data is not None:
            self.send_app_type_comvalue.set(self.data['sendAppName'])
        else:
            self.send_app_type_comboxlist.current(0)

        self.send_app_type_comboxlist.bind("<<ComboboxSelected>>", self.send_app_type_on_change)
        self.send_app_type_comboxlist.unbind_class("TCombobox", "<MouseWheel>")
        self.send_app_type_comboxlist.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(5, 5), fill='y')

        split_line = Frame(self.parent, height=1, relief=GROOVE,
                           highlightthickness=1, highlightbackground="#F0F0F0", highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')

        frame2 = Frame(self.parent, height=100, width=100, bg='white', borderwidth=1)
        frame2.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        send_contacts = get_rpa_contact(self.app_type[self.send_app_type_comvalue.get()])['data']

        if self.data is not None:
            self.send_contact_list_frame = ContactListFrame(frame2, send_contacts, self.send_app_type_comvalue.get(),
                                                            selected_contacts=self.data['sendContactList'])
        else:
            self.send_contact_list_frame = ContactListFrame(frame2, send_contacts, self.send_app_type_comvalue.get())

        NewContactFrame(frame2, self.app_type, self.send_app_type_comvalue, self.send_contact_list_frame, self). \
            pack(side=TOP, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y', expand=True)

        self.send_contact_list_frame.pack(side=TOP, anchor=NW, padx=(30, 0), pady=(10, 5), fill='y')
        split_line = Frame(frame2, height=1, relief=GROOVE, highlightthickness=1, highlightbackground="#F0F0F0",
                           highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(10, 0), fill='x')

    def init_frame2(self):
        frame1 = Frame(self.parent, height=40, width=100, bg='white', borderwidth=1)
        frame1.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 1), fill='x')

        receive_app_type_label = Label(frame1, width=10, text='发送到', bg='white', anchor='w')
        receive_app_type_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        self.receive_app_type_comvalue = StringVar()
        self.receive_app_type_comboxlist = Combobox(frame1, state="readonly",
                                                    textvariable=self.receive_app_type_comvalue)
        self.receive_app_type_comboxlist["values"] = tuple(self.app_type.keys())
        if self.data is not None:
            self.receive_app_type_comvalue.set(self.data['receiveAppName'])
        else:
            self.receive_app_type_comboxlist.current(0)

        self.receive_app_type_comboxlist.bind("<<ComboboxSelected>>", self.receive_app_type_on_change)
        self.receive_app_type_comboxlist.unbind_class("TCombobox", "<MouseWheel>")
        self.receive_app_type_comboxlist.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(5, 5), fill='y')

        frame2 = Frame(self.parent, height=100, width=100, bg='white', borderwidth=1)
        frame2.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        receive_contacts = get_rpa_contact(self.app_type[self.receive_app_type_comvalue.get()])['data']
        if self.data is not None:
            self.receive_contact_list_frame = ContactListFrame(frame2, receive_contacts,
                                                               self.receive_app_type_comvalue.get(),
                                                               selected_contacts=self.data['receiveContactList'])
        else:
            self.receive_contact_list_frame = ContactListFrame(frame2, receive_contacts,
                                                               self.receive_app_type_comvalue.get())

        NewContactFrame(frame2, self.app_type, self.receive_app_type_comvalue, self.receive_contact_list_frame, self). \
            pack(side=TOP, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y', expand=True)

        self.receive_contact_list_frame.pack(side=TOP, anchor=NW, padx=(30, 0), pady=(10, 5), fill='y')

        split_line = Frame(frame2, height=1, relief=GROOVE, highlightthickness=1, highlightbackground="#F0F0F0",
                           highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(10, 0), fill='x')

        keyword_list = get_keyword_list()['data']
        if self.data is not None:
            self.keyword_list_frame = KeywordListFrame(frame2, keyword_list, selected_keywords=self.data['keywords'])
        else:
            self.keyword_list_frame = KeywordListFrame(frame2, keyword_list)

        NewKeywordFrame(frame2, self.keyword_list_frame, self). \
            pack(side=TOP, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y', expand=True)
        self.keyword_list_frame.pack(side=TOP, anchor=NW, padx=(30, 0), pady=(10, 10), fill='y')

    def init_btn_frame(self):
        btn_frame = Frame(self.parent, borderwidth=1, bg='white')
        btn_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 10), fill='both')

        SplitLine(btn_frame)
        self.receive_status_style = Style()
        self.receive_status_style.configure('Receive.TRadiobutton', background='white')
        self.receive_status_flag = 0
        self.receive_status_radio = Radiobutton(btn_frame, text='接受更多潜在相似信息', width=18, command=self.receive_status_radio_click,
                                        style='Receive.TRadiobutton')
        self.receive_status_radio.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        if self.data is not None and self.data['receiveStatus'] == 1:
            self.receive_status_radio.state(["selected"])
            self.receive_status_flag = 1
        else:
            self.receive_status_radio.state(["!focus", "!selected"])

        self.cancel_btn_image = ImageTk.PhotoImage(
            Image.open(Config.cancel_btn).resize((50, 23), Image.ANTIALIAS))
        self.cancel_btn = Button(btn_frame, image=self.cancel_btn_image, borderwidth=0, bg='white',
                                 command=lambda: self.reset_repeater_list())
        self.cancel_btn.pack(side=RIGHT, anchor=NW, padx=(10, 20), pady=(5, 5), fill='y')

        self.confirm_btn_image = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))
        confirm_btn = Button(btn_frame, image=self.confirm_btn_image, borderwidth=0, bg='white', command=self.add_repeater_data)
        if self.data is not None:
            confirm_btn['command'] = self.update_repeater_data
        confirm_btn.pack(side=RIGHT, anchor=NW, padx=(0, 0), pady=(5, 5), fill='y')

    def receive_status_radio_click(self):
        if self.receive_status_flag == 1:
            self.receive_status_flag = 0
        else:
            self.receive_status_flag = 1
        self.set_radio_state()

    def set_radio_state(self):
        if self.receive_status_flag == 0:
            self.receive_status_radio.state(["!focus", "!selected"])
        else:
            self.receive_status_radio.state(["selected"])

    def add_repeater_data(self):
        if not get_login_status(self.setting_frame.parent):
            return

        selected_send_contacts = self.send_contact_list_frame.get_selected_contacts()
        selected_receive_contacts = self.receive_contact_list_frame.get_selected_contacts()
        selected_keywords = self.keyword_list_frame.get_selected_keyword()
        if len(selected_send_contacts) == 0 or len(selected_receive_contacts) == 0 or len(selected_keywords) == 0:
            return

        data = {
            "sendAppId": self.app_type[self.send_app_type_comvalue.get()],
            "sendContactIdList": selected_send_contacts,
            "receiveAppId": self.app_type[self.receive_app_type_comvalue.get()],
            "receiveContactIdList": selected_receive_contacts,
            "keywordIdList": self.keyword_list_frame.get_selected_keyword(),
            "receiveStatus": self.receive_status_flag,
            "id": -1,
        }

        add_repeater(data)
        self.reset_repeater_list()

    def update_repeater_data(self):
        if not get_login_status(self.setting_frame.parent):
            return

        selected_send_contacts = self.send_contact_list_frame.get_selected_contacts()
        selected_receive_contacts = self.receive_contact_list_frame.get_selected_contacts()
        selected_keywords = self.keyword_list_frame.get_selected_keyword()
        if len(selected_send_contacts) == 0 or len(selected_receive_contacts) == 0 or len(selected_keywords) == 0:
            return

        data = {
            "sendAppId": self.app_type[self.send_app_type_comvalue.get()],
            "sendContactIdList": selected_send_contacts,
            "receiveAppId": self.app_type[self.receive_app_type_comvalue.get()],
            "receiveContactIdList": selected_receive_contacts,
            "keywordIdList": self.keyword_list_frame.get_selected_keyword(),
            "id": self.data['id'],
            "channelId": self.data['channelId'],
            "receiveStatus": self.receive_status_flag
        }
        update_repeater(data)
        self.reset_repeater_list()

    def reset_repeater_list(self):
        self.setting_frame.reset_repeater_list_frame()

    def send_app_type_on_change(self, event):
        choice = event.widget.get()
        if choice == '微信':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'QQ':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '钉钉':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '微博':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '陌陌':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '钉钉6':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '前程无忧':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'WhatsApp':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'LINE':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        self.send_contact_list_frame.change_contacts(contacts)

    def receive_app_type_on_change(self, event):
        choice = event.widget.get()
        if choice == '微信':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'QQ':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '钉钉':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '微博':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '陌陌':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '钉钉6':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == '前程无忧':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'WhatsApp':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        elif choice == 'LINE':
            contacts = get_rpa_contact(self.app_type[choice])['data']
        self.receive_contact_list_frame.change_contacts(contacts)
