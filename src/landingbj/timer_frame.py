# cython: language_level=3
from datetime import datetime
from tkinter import Frame, TOP, Label, NW, GROOVE, Button, SE, StringVar, Entry, END, NORMAL, Text, LEFT, NE, RIGHT
from tkinter.ttk import Combobox, Radiobutton, Style

from PIL import ImageTk, Image

from landingbj.config import Config
from landingbj.gui_module import DateEntry, ContactListFrame, NewContactFrame, ImageBrowserFrame, SplitLine
from landingbj.message_box import get_login_status
from landingbj.qa import get_app_type_list, get_rpa_contact, add_timer_task, update_timer_task, delete_timer_task
from landingbj.util import get_image


class TimerFrame(Frame):
    def __init__(self, parent, height, width, data, setting_frame):
        super().__init__(parent)
        self.setting_frame = setting_frame
        self.parent = parent
        self.data = data

        if self.data['appId'] in Config.selected_app_type:
            bg_color = 'white'
        else:
            bg_color = '#dcdcdc'

        item_frame = Frame(parent, height=height, width=width, bg=bg_color, borderwidth=1)
        item_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=10, padx=5)

        title_frame = Frame(item_frame, height=33, width=width, bg=bg_color, borderwidth=1)
        self.app_icon = get_image(self.data['appIcon'])
        app_icon_label = Label(title_frame, bg=bg_color, image=self.app_icon)
        app_icon_label.pack(side=LEFT, anchor=NW, fill='y', pady=3, padx=(5, 0))

        app_name_label = Label(title_frame, text=self.data['appType'], bg=bg_color)
        app_name_label.pack(side=LEFT, anchor=NW, fill='y', pady=3, padx=(3, 0))

        self.delete_btn_image = ImageTk.PhotoImage(
            Image.open(Config.delete_btn).resize((50, 23), Image.ANTIALIAS))
        delete_btn = Button(title_frame, image=self.delete_btn_image, bg=bg_color, borderwidth=0,
                            command=lambda: self.delete_timer_data(data['id']))
        delete_btn.pack(side=RIGHT, anchor=NE, fill='y', pady=3, padx=(20, 15))

        self.update_btn_image = ImageTk.PhotoImage(
            Image.open(Config.update_btn).resize((50, 23), Image.ANTIALIAS))
        update_btn = Button(title_frame, image=self.update_btn_image, bg=bg_color, borderwidth=0,
                            command=lambda: self.show_update_frame(data['id']))
        update_btn.pack(side=RIGHT, anchor=NE, fill='y', pady=3, padx=(0, 0))
        title_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=0)

        split_line = Frame(item_frame, height=1, relief=GROOVE,
                           highlightthickness=1, highlightbackground="#F0F0F0", highlightcolor="#F0F0F0")
        split_line.pack()
        split_line.place(relwidth=1, x=0, y=34)

        if len(self.data['imageList']) > 0:
            self.timer_image = get_image(self.data['imageList'][0], size=(75, 75))
        else:
            self.timer_image = ImageTk.PhotoImage(
                Image.open(Config.timer_placeholder).resize((75, 75), Image.ANTIALIAS))

        detail_frame = Frame(item_frame, width=width, bg=bg_color, borderwidth=1)

        timer_image_label = Label(detail_frame, image=self.timer_image, bg=bg_color)
        timer_image_label.pack(side=LEFT, anchor=NW, fill='both', pady=0, padx=(10, 10))

        message_label = Label(detail_frame, anchor='w', text=self.data['message'], bg=bg_color)
        message_label.pack(side=TOP, anchor=NW, fill='x', expand=True, pady=0, padx=0)

        time_frame = Frame(detail_frame, height=33, width=width, bg=bg_color, borderwidth=1)
        time_frame.pack(side=TOP, anchor=NW, fill='x', expand=True, pady=0, padx=0)

        self.time_icon = ImageTk.PhotoImage(Image.open(Config.time_icon).resize((13, 13), Image.ANTIALIAS))
        time_icon_label = Label(time_frame, image=self.time_icon, bg=bg_color)
        time_icon_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=0)

        time = datetime.strptime(self.data['sendTime'], '%b %d, %Y %I:%M:%S %p').strftime('%Y-%m-%d %H:%M:%S')
        time_label = Label(time_frame, text=time, bg=bg_color, fg='#7B7B7B')
        time_label.config(font=('None', 8))
        time_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=0)

        if self.data['repeatFlag'] == 0:
            repeat_text = '不重复'
        else:
            repeat_text = '重复 ' + str(self.data['repeatDay']) + '天' + str(self.data['repeatHour']) + '时' + str(
                self.data['repeatMinute']) + '分'
        repeat_label = Label(time_frame, text=repeat_text, bg=bg_color, fg='#7B7B7B')
        repeat_label.config(font=('None', 8))
        repeat_label.pack(side=LEFT, anchor=NW, fill='x', expand=True, pady=0, padx=0)

        contact_frame = Frame(detail_frame, height=33, width=width, bg=bg_color, borderwidth=1)
        contact_frame.pack(side=TOP, anchor=NW, fill='x', expand=True, pady=0, padx=0)

        self.contact_icon = ImageTk.PhotoImage(Image.open(Config.contact_icon).resize((13, 13), Image.ANTIALIAS))
        contact_icon_label = Label(contact_frame, image=self.contact_icon, bg=bg_color)
        contact_icon_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=0)

        contact = ' '.join(map(str, self.data['contactNameList']))
        contact_label = Label(contact_frame, text=contact, bg=bg_color, fg='#7B7B7B')
        contact_label.config(font=('None', 8))
        contact_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=0)

        detail_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=(10, 10), padx=0)

    def show_update_frame(self, id):
        self.setting_frame.show_timer_update_frame(id)

    def delete_timer_data(self, data_id):
        if not get_login_status(self.setting_frame.parent):
            return

        result = delete_timer_task(data_id)
        if result['status'] == 'success':
            self.setting_frame.reset_timer_list_frame()


class TimerAddOrUpdateFrame(Frame):
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

        app_type_label = Label(frame1, width=10, text='软件类型', bg='white', anchor='w')
        app_type_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(10, 5), fill='y')

        self.app_type_comvalue = StringVar()
        self.app_type_comboxlist = Combobox(frame1, state="readonly", textvariable=self.app_type_comvalue)
        self.app_type_comboxlist["values"] = tuple(self.app_type.keys())
        if self.data is not None:
            self.app_type_comvalue.set(self.data['appType'])
        else:
            self.app_type_comboxlist.current(0)

        self.app_type_comboxlist.bind("<<ComboboxSelected>>", self.app_type_on_change)
        self.app_type_comboxlist.unbind_class("TCombobox", "<MouseWheel>")
        self.app_type_comboxlist.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(5, 5), fill='y')

        SplitLine(self.parent)

        frame2 = Frame(self.parent, height=100, width=100, bg='white', borderwidth=1)
        frame2.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        send_date_label = Label(frame2, width=10, text='发送时间', bg='white', anchor='w')
        send_date_label.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        send_date_frame = Frame(frame2, bg='#F4F6F8', borderwidth=4)
        send_date_frame.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(5, 5), fill='both')
        if self.data is not None:
            self.send_date = DateEntry(send_date_frame, date_str=self.data['sendTime'], font=('Helvetica', 10, NORMAL),
                                       border=0)
        else:
            self.send_date = DateEntry(send_date_frame, font=('Helvetica', 10, NORMAL), border=0)
        self.send_date.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(2, 2), fill='y')
        SplitLine(self.parent)

        frame3 = Frame(self.parent, height=100, width=100, bg='white', borderwidth=1)
        frame3.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        self.repeat_radio_style = Style()
        self.repeat_radio_style.configure('Repeat.TRadiobutton', background='white')
        self.repeat_radio_flag = 0
        self.repeat_radio = Radiobutton(frame3, text='重复', width=9, command=self.repeat_radio_click,
                                        style='Repeat.TRadiobutton')
        self.repeat_radio.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        if self.data is not None and self.data['repeatFlag'] == 1:
            self.repeat_radio.state(["selected"])
            self.repeat_radio_flag = 1
        else:
            self.repeat_radio.state(["!focus", "!selected"])

        interval_label = Label(frame3, text='间隔', bg='white')
        interval_label.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(5, 5), fill='both')

        self.day_entry = Entry(frame3, width=3, bg='#F4F6F8', borderwidth=0, justify='right')
        self.day_entry.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')
        self.day_entry.insert(0, 0)

        day_label = Label(frame3, text='天', bg='white')
        day_label.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')

        self.hour_entry = Entry(frame3, width=4, bg='#F4F6F8', borderwidth=0, justify='right')
        self.hour_entry.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')
        self.hour_entry.insert(0, 0)

        hour_label = Label(frame3, text='时', bg='white')
        hour_label.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')

        self.minute_entry = Entry(frame3, width=4, bg='#F4F6F8', borderwidth=0, justify='right')
        self.minute_entry.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')
        self.minute_entry.insert(0, 0)

        minute_label = Label(frame3, text='分', bg='white')
        minute_label.pack(side=LEFT, anchor=NW, padx=(3, 0), pady=(5, 5), fill='both')

        SplitLine(self.parent)

        self.day_entry.bind('<KeyRelease>', lambda e: self._check_day())
        self.hour_entry.bind('<KeyRelease>', lambda e: self._check_hour())
        self.minute_entry.bind('<KeyRelease>', lambda e: self._check_minute())

        self.day_entry.bind('<FocusOut>', lambda e: self._check_blank(self.day_entry))
        self.hour_entry.bind('<FocusOut>', lambda e: self._check_blank(self.hour_entry))
        self.minute_entry.bind('<FocusOut>', lambda e: self._check_blank(self.minute_entry))

        if self.data is not None:
            self.day_entry.delete(0, END)
            self.hour_entry.delete(0, END)
            self.minute_entry.delete(0, END)
            self.day_entry.insert(0, self.data['repeatDay'])
            self.hour_entry.insert(0, self.data['repeatHour'])
            self.minute_entry.insert(0, self.data['repeatMinute'])

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, END)
        entry.insert(0, cont[:-1])

    def _check_day(self):
        day = self.day_entry.get()
        if not day.isdigit() or len(day) > 2:
            self._backspace(self.day_entry)

    def _check_hour(self):
        hour = self.hour_entry.get()
        if not hour.isdigit() or int(hour) > 59:
            self._backspace(self.hour_entry)

    def _check_minute(self):
        minute = self.minute_entry.get()
        if not minute.isdigit() or int(minute) > 59:
            self._backspace(self.minute_entry)

    def _check_blank(self, entry):
        data = entry.get()

        if len(data) == 0:
            entry.insert(0, 0)

    def init_frame2(self):
        frame2 = Frame(self.parent, height=100, width=100, bg='white', borderwidth=1)
        frame2.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 0), fill='x')

        contacts = get_rpa_contact(self.app_type[self.app_type_comvalue.get()])['data']
        if self.data is not None:
            self.contactListFrame = ContactListFrame(frame2, contacts, self.app_type_comvalue.get(),
                                                     selected_contacts=self.data['contactList'])
        else:
            self.contactListFrame = ContactListFrame(frame2, contacts, self.app_type_comvalue.get())

        NewContactFrame(frame2, self.app_type, self.app_type_comvalue, self.contactListFrame, self). \
            pack(side=TOP, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y', expand=True)

        SplitLine(frame2)

        self.contactListFrame.pack(side=TOP, anchor=NW, padx=(30, 0), pady=(10, 10), fill='y')

        SplitLine(frame2)

        self.entry_message_input = Text(frame2, fg='#7B7B7B', bg='#F4F6F8', width=39, height=5, relief='flat',
                                        borderwidth=4)
        if self.data is not None:
            self.entry_message_input.insert(1.0, self.data['message'])
        self.entry_message_input.pack(side=TOP, anchor=NW, padx=(35, 0), pady=(10, 10), fill='y')

        SplitLine(frame2)

        if self.data is not None:
            self.image_browser_frame = ImageBrowserFrame(frame2, self.data['imageList'])
        else:
            self.image_browser_frame = ImageBrowserFrame(frame2)
        self.image_browser_frame.pack(side=TOP, anchor=NW, padx=(35, 0), pady=(10, 10), fill='y')

    def init_btn_frame(self):
        btn_frame = Frame(self.parent, borderwidth=1, bg='white')
        btn_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 10), fill='x')
        SplitLine(btn_frame)
        self.spread_status_style = Style()
        self.spread_status_style.configure('Spread.TRadiobutton', background='white')
        self.spread_status_flag = 0
        self.spread_status_radio = Radiobutton(btn_frame, text='扩散更多潜在兴趣人群', width=18, command=self.spread_status_radio_click,
                                        style='Spread.TRadiobutton')
        self.spread_status_radio.pack(side=LEFT, anchor=NW, padx=(30, 0), pady=(5, 5), fill='y')

        if self.data is not None and self.data['spreadStatus'] == 1:
            self.spread_status_radio.state(["selected"])
            self.spread_status_flag = 1
        else:
            self.spread_status_radio.state(["!focus", "!selected"])

        self.cancel_btn_image = ImageTk.PhotoImage(
            Image.open(Config.cancel_btn).resize((50, 23), Image.ANTIALIAS))
        self.cancel_btn = Button(btn_frame, image=self.cancel_btn_image, borderwidth=0, bg='white',
                                 command=lambda: self.reset_timer_list())
        self.cancel_btn.pack(side=RIGHT, anchor=NW, padx=(10, 20), pady=(5, 5), fill='y')

        self.confirm_btn_image = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))
        confirm_btn = Button(btn_frame, bg='white', image=self.confirm_btn_image, borderwidth=0, command=self.add_timer_data)
        if self.data is not None:
            confirm_btn['command'] = self.update_timer_data
        confirm_btn.pack(side=RIGHT, anchor=NW, padx=(0, 0), pady=(5, 5), fill='y')

    def add_timer_data(self):
        if not get_login_status(self.setting_frame.parent):
            return

        selected_contacts = self.contactListFrame.get_selected_contacts()
        if len(selected_contacts) == 0:
            return
        message = self.entry_message_input.get(1.0, END).strip()
        if len(message) == 0:
            self.entry_message_input.focus()
            return
        data = {'id': '-1',
                'appId': self.app_type[self.app_type_comvalue.get()],
                'sendTime': self.send_date.get(),
                'repeatFlag': self.repeat_radio_flag,
                'repeatDay': self.day_entry.get(),
                'repeatHour': self.hour_entry.get(),
                'repeatMinute': self.minute_entry.get(),
                'contactIdList': self.contactListFrame.get_selected_contacts(),
                'spreadStatus': self.spread_status_flag,
                'message': self.entry_message_input.get(1.0, END).strip()}
        image_files = self.image_browser_frame.get_upload_images()
        add_timer_task(data, image_files)
        self.reset_timer_list()

    def update_timer_data(self):
        if not get_login_status(self.setting_frame.parent):
            return

        selected_contacts = self.contactListFrame.get_selected_contacts()
        if len(selected_contacts) == 0:
            return
        message = self.entry_message_input.get(1.0, END).strip()
        if len(message) == 0:
            self.entry_message_input.focus()
            return
        data = {'id': self.data['id'],
                'appId': self.app_type[self.app_type_comvalue.get()],
                'sendTime': self.send_date.get(),
                'repeatFlag': self.repeat_radio_flag,
                'repeatDay': self.day_entry.get(),
                'repeatHour': self.hour_entry.get(),
                'repeatMinute': self.minute_entry.get(),
                'contactIdList': selected_contacts,
                'spreadStatus': self.spread_status_flag,
                'message': self.entry_message_input.get(1.0, END).strip(),
                'deleted_images': self.image_browser_frame.get_delete_images()}
        image_files = self.image_browser_frame.get_upload_images()
        update_timer_task(data, image_files)
        self.reset_timer_list()

    def reset_timer_list(self):
        # self.setting_frame.reset_selector_frame()
        self.setting_frame.reset_timer_list_frame()

    def repeat_radio_click(self):
        if self.repeat_radio_flag == 1:
            self.repeat_radio_flag = 0
        else:
            self.repeat_radio_flag = 1
        self.set_radio_state()

    def spread_status_radio_click(self):
        if self.spread_status_flag == 1:
            self.spread_status_flag = 0
        else:
            self.spread_status_flag = 1
        self.set_radio_state()

    def set_radio_state(self):
        if self.repeat_radio_flag == 0:
            self.repeat_radio.state(["!focus", "!selected"])
        else:
            self.repeat_radio.state(["selected"])

        if self.spread_status_flag == 0:
            self.spread_status_radio.state(["!focus", "!selected"])
        else:
            self.spread_status_radio.state(["selected"])

    def app_type_on_change(self, event):
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

        self.contactListFrame.change_contacts(contacts)
