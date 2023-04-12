# cython: language_level=3
import json
import webbrowser
from tkinter import Toplevel, Label, Frame, PhotoImage, Button, LEFT, StringVar, Entry, TOP, NW, RIGHT, CENTER, END
from tkinter.font import Font

from landingbj import qa, autogui
from landingbj.config import Config
from landingbj.util import encode_login_status, get_current_settings, check_login_status


class DialCheckMessagebox(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        dpi_value = self.winfo_fpixels('1i')
        scale_ratio = round(dpi_value / 96.0, 2)
        monitor_region = autogui.get_monitor_region()
        x, y = monitor_region[0] + 380, monitor_region[1] + 380
        self.geometry('%dx%d+%d+%d' % (240 * scale_ratio, 120 * scale_ratio, x, y))
        self.resizable(0, 0)
        self.title('校准精度')
        self.message = 'continue'

        label_channel_name = Label(self, anchor="center", text='抱歉，并未有效选择聊天软件区域')

        label_channel_name.pack(fill='x', pady=20)
        button_frame = Frame(self)
        button_frame.pack(padx=10)
        self.continue_icon = PhotoImage(file=Config.continue_icon).subsample(3, 3)
        continue_btn = Button(button_frame, compound=LEFT, image=self.continue_icon, text=' 继续 ? ', command=self.go_on)
        continue_btn.grid(row=0, column=0, padx=(0, 20))
        self.retry_icon = PhotoImage(file=Config.retry_icon).subsample(3, 3)
        retry_btn = Button(button_frame, compound=LEFT, image=self.retry_icon, text=' 重来 X ', command=self.retry)
        retry_btn.grid(row=0, column=1, padx=(20, 0))

        self.master.call("wm", "attributes", ".", "-topmost", "false")
        self.attributes("-topmost", "true")
        self.grab_set()

    def go_on(self):
        self.destroy()

    def retry(self):
        self.destroy()
        self.message = 'retry'


class LoginMessagebox(Toplevel):
    def __init__(self, master):
        super().__init__(master)
        dpi_value = self.winfo_fpixels('1i')
        scale_ratio = round(dpi_value / 96.0, 2)
        self.geometry('%dx%d+680+380' % (300 * scale_ratio, 135 * scale_ratio))
        self.resizable(0, 0)
        self.title('私人定制')
        self.status = False

        prompt = '您专属通道' + Config.channel_name + '下用户' + Config.channel_user + '的密码：'

        frame1 = Frame(self)
        password_input_label = Label(frame1, text=prompt, bd=0)
        password_input_label.config(font=('Helvetica', 9))
        password_input_label.pack(side=TOP, anchor=NW, fill='none', pady=(0, 0), padx=0)

        self.password = StringVar()
        self.entry_password = Entry(frame1, show="*", width=30, borderwidth=0, textvariable=self.password, fg='black')
        self.entry_password.pack(side=TOP, anchor=NW, fill='x', pady=(8, 0), padx=(0, 0))
        frame1.pack(side=TOP, anchor=CENTER, fill='none', pady=(10, 0), padx=0)

        frame2 = Frame(self)
        self.confirm_icon = PhotoImage(file=Config.continue_icon).subsample(3, 3)
        continue_btn = Button(frame2, compound=LEFT, image=self.confirm_icon, text='  确定  ', command=self.confirm)
        continue_btn.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=(0, 0))
        self.cancel_icon = PhotoImage(file=Config.retry_icon).subsample(3, 3)
        cancel_btn = Button(frame2, compound=LEFT, image=self.cancel_icon, text='  取消  ', command=self.cancel)
        cancel_btn.pack(side=RIGHT, anchor=NW, fill='x', pady=0, padx=(0, 0))
        frame2.pack(side=TOP, anchor=CENTER, fill='x', pady=(10, 0), padx=(70 * scale_ratio, 70 * scale_ratio))

        frame3 = Frame(self)
        self.register_label = Label(frame3, anchor='nw', compound='left', text='一键生成', bd=0)
        self.register_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=(0, 0))
        self.saas_url_label = Label(frame3, anchor='nw', compound='left', text='http://saas.landingbj.com', bd=0,
                                    cursor="hand2")
        self.saas_url_label.config(font=('Helvetica', 9))
        self.saas_url_label.pack(side=LEFT, anchor=NW, fill='x', pady=0, padx=(0, 0))
        self.saas_url_label.bind("<Button-1>", self.open_url)
        font = Font(self.saas_url_label, self.saas_url_label.cget("font"))
        font.configure(underline=True)
        self.register_label.config(font=('Helvetica', 9))
        self.saas_url_label.configure(font=font)
        frame3.pack(side=TOP, anchor=CENTER, pady=(15, 0), padx=(0, 0))

    def confirm(self):
        pwd = self.password.get()
        if len(pwd.strip()) == 0:
            self.entry_password.focus()
            return
        data = {'username': Config.channel_user, 'password': pwd}
        result = qa.login(data)
        if result['status'] == 'success':
            config = get_current_settings()
            config['login_status'] = encode_login_status(Config.channel_name, Config.channel_user)
            Config.login_status = config['login_status']
            with open('config.json', 'w') as outfile:
                json.dump(config, outfile, sort_keys=True, indent=4)
            self.status = True
            self.destroy()
        else:
            self.entry_password.select_range(0, END)
            self.entry_password.icursor(END)

    def cancel(self):
        self.destroy()

    def open_url(self, event):
        webbrowser.open('http://saas.landingbj.com', new=2)


def get_login_status(master):
    if not check_login_status(Config.channel_name, Config.channel_user, Config.login_status):
        master.call("wm", "attributes", ".", "-topmost", "false")
        login_message_box = LoginMessagebox(master)
        master.wait_window(login_message_box)
        master.call("wm", "attributes", ".", "-topmost", "true")
        status = login_message_box.status
        return status
    return True
