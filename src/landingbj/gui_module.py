# cython: language_level=3
from datetime import datetime
from sys import platform
from tkinter import Canvas, Frame, Label, NW, Button, LEFT, Entry, END, filedialog, Toplevel, GROOVE, TOP
from tkinter.ttk import Scrollbar
from urllib.parse import urlparse

from PIL import ImageTk, Image

from landingbj.config import Config
from landingbj.message_box import get_login_status
from landingbj.qa import get_image_by_url, get_rpa_contact, add_app_contact, add_app_keyword, get_keyword_list


class ScrollFrame(Frame):
    def __init__(self, parent, setting_detail_frame=None):
        super().__init__(parent)
        self.parent = parent
        self.canvas = Canvas(self, borderwidth=0, highlightthickness=0, background="#F0F0F0")
        self.viewPort = Frame(self.canvas, background="#F0F0F0")

        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((4, 4), window=self.viewPort, anchor="nw", tags="self.viewPort")
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        self.viewPort.bind('<Enter>', self.onEnter)
        self.viewPort.bind('<Leave>', self.onLeave)
        self.onFrameConfigure(None)

        self.setting_detail_frame = setting_detail_frame

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def onMouseWheel(self, event):
        if self.viewPort.winfo_height() <= self.parent.winfo_height():
            return
        if self.setting_detail_frame is not None and self.vsb.get()[1] == 1.0:
            self.setting_detail_frame.update_qa_list_frame()
            self.onEnter(event=None)
        if platform == 'win32':
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform == 'darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def onEnter(self, event):
        if platform == 'linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):
        if platform == 'linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")


class GuiCache:
    qa_data_cache = {}
    timer_data_cache = {}
    repeater_data_cache = {}


class DateEntry(Frame):
    def __init__(self, master, date_str=None, frame_look={}, **look):
        args = dict()
        args.update(frame_look)
        Frame.__init__(self, master, **args)

        args = {}
        args.update(look)
        if date_str is None:
            send_time = datetime.now()
        else:
            send_time = datetime.strptime(date_str, '%b %d, %Y %I:%M:%S %p')
        self.entry_1 = Entry(self, width=4, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_1.insert(END, send_time.year)
        self.label_1 = Label(self, text='-', **args, bg='#F4F6F8', borderwidth=0)
        self.entry_2 = Entry(self, width=2, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_2.insert(END, send_time.month)
        self.label_2 = Label(self, text='-', **args, bg='#F4F6F8', borderwidth=0)
        self.entry_3 = Entry(self, width=2, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_3.insert(END, send_time.day)
        self.label_4 = Label(self, text=' ', **args, bg='#F4F6F8', borderwidth=0)
        self.entry_4 = Entry(self, width=2, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_4.insert(END, send_time.hour)
        self.label_5 = Label(self, text=':', **args, bg='#F4F6F8', borderwidth=0)
        self.entry_5 = Entry(self, width=2, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_5.insert(END, send_time.minute)
        self.label_6 = Label(self, text=':', **args, bg='#F4F6F8', borderwidth=0)
        self.entry_6 = Entry(self, width=2, **args, bg='#F4F6F8', borderwidth=0)
        self.entry_6.insert(END, send_time.second)

        self.entry_1.pack(side=LEFT)
        self.label_1.pack(side=LEFT)
        self.entry_2.pack(side=LEFT)
        self.label_2.pack(side=LEFT)
        self.entry_3.pack(side=LEFT)
        self.label_4.pack(side=LEFT)
        self.entry_4.pack(side=LEFT)
        self.label_5.pack(side=LEFT)
        self.entry_5.pack(side=LEFT)
        self.label_6.pack(side=LEFT)
        self.entry_6.pack(side=LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3, self.entry_4, self.entry_5, self.entry_6]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 4))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 2))
        self.entry_4.bind('<KeyRelease>', lambda e: self._check(3, 2))
        self.entry_5.bind('<KeyRelease>', lambda e: self._check(4, 2))
        self.entry_6.bind('<KeyRelease>', lambda e: self._check(5, 2))

        self.entry_1.bind('<FocusOut>', lambda e: self._check_blank(0))
        self.entry_2.bind('<FocusOut>', lambda e: self._check_blank(1))
        self.entry_3.bind('<FocusOut>', lambda e: self._check_blank(2))
        self.entry_4.bind('<FocusOut>', lambda e: self._check_blank(3))
        self.entry_5.bind('<FocusOut>', lambda e: self._check_blank(4))
        self.entry_6.bind('<FocusOut>', lambda e: self._check_blank(5))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def _check_blank(self, index):
        entry = self.entries[index]
        data = entry.get()

        if len(data) == 0:
            entry.insert(0, 0)

    def get(self):
        return self.entry_1.get() + '-' + self.entry_2.get() + '-' + self.entry_3.get() + ' ' \
               + self.entry_4.get() + ':' + self.entry_5.get() + ':' + self.entry_6.get()


class ContactListFrame(Frame):
    def __init__(self, parent, contacts, app_type, selected_contacts=None):
        super().__init__(parent, bg='white')
        self.columnconfigure(0, weight=1)
        self.contact_label_list = []
        self.contact_idx_dict = {}
        self.set_contacts(contacts)
        self.contacts = contacts
        self.selected_contacts = selected_contacts
        self.app_type = app_type

        if selected_contacts is not None:
            for a in selected_contacts:
                idx = self.contact_idx_dict[a['contactName']]
                self.contact_label_list[idx]['bg'] = '#408CFB'
                self.contact_label_list[idx]['fg'] = 'white'

    def update_contact(self, contacts, app_type):
        self.clean_contact_label()
        self.contact_label_list = []
        self.contact_idx_dict = {}
        self.set_contacts(contacts)
        self.contacts = contacts
        if app_type == self.app_type:
            if self.selected_contacts is not None:
                for a in self.selected_contacts:
                    idx = self.contact_idx_dict[a['contactName']]
                    self.contact_label_list[idx]['bg'] = '#408CFB'
                    self.contact_label_list[idx]['fg'] = 'white'
        else:
            self.app_type = app_type

    def contact_click(self, idx):
        if self.contact_label_list[idx]['bg'] == '#F4F6F8':
            self.contact_label_list[idx]['bg'] = '#408CFB'
            self.contact_label_list[idx]['fg'] = 'white'
        else:
            self.contact_label_list[idx]['bg'] = '#F4F6F8'
            self.contact_label_list[idx]['fg'] = 'black'

    def set_contacts(self, contacts):
        i, j = 0, 0
        self.contact_label_list = []
        self.contacts = contacts
        for idx, contact in enumerate(contacts):
            contact_label = Label(self, text=contact['contactName'], width=11, bg='#F4F6F8', relief='flat',
                                  borderwidth=4)
            self.contact_label_list.append(contact_label)
            contact_label.bind("<Button-1>", lambda e, idx=idx: self.contact_click(idx))
            if j % 3 == 0 and j > 0:
                i, j = i + 1, 0
            contact_label.grid(row=i, column=j, sticky='e', pady=(2, 2), padx=(5, 5))
            j = j + 1
            self.contact_idx_dict[contact['contactName']] = idx

    def clean_contact_label(self):
        for label in self.contact_label_list:
            label.destroy()
        self.contact_idx_dict = {}

    def change_contacts(self, contacts):
        self.clean_contact_label()
        self.contact_label_list = []
        self.set_contacts(contacts)

    def get_selected_contacts(self):
        selected_contact_ids = []
        for label in self.contact_label_list:
            if label['bg'] == '#408CFB':
                selected_contact_ids.append(self.contacts[self.contact_idx_dict[label['text']]]['id'])
        return selected_contact_ids


class KeywordListFrame(Frame):
    def __init__(self, parent, keywords, selected_keywords=None):
        super().__init__(parent, bg='white')
        self.columnconfigure(0, weight=1)

        self.keyword_label_list = []
        self.keyword_idx_dict = {}
        self.set_keywords(keywords)
        self.keywords = keywords
        self.selected_keywords = selected_keywords

        if selected_keywords is not None:
            for a in selected_keywords:
                idx = self.keyword_idx_dict[a['keyword']]
                self.keyword_label_list[idx]['bg'] = '#408CFB'
                self.keyword_label_list[idx]['fg'] = 'white'

    def update_keywords(self, keywords):
        self.clean_keyword_label()
        self.keyword_label_list = []
        self.keyword_idx_dict = {}
        self.set_keywords(keywords)
        self.keywords = keywords
        if self.selected_keywords is not None:
            for a in self.selected_keywords:
                idx = self.keyword_idx_dict[a['keyword']]
                self.keyword_label_list[idx]['bg'] = '#408CFB'
                self.keyword_label_list[idx]['fg'] = 'white'

    def keyword_click(self, idx):
        if self.keyword_label_list[idx]['bg'] == '#F4F6F8':
            self.keyword_label_list[idx]['bg'] = '#408CFB'
            self.keyword_label_list[idx]['fg'] = 'white'
        else:
            self.keyword_label_list[idx]['bg'] = '#F4F6F8'
            self.keyword_label_list[idx]['fg'] = 'black'

    def set_keywords(self, keywords):
        i, j = 0, 0
        self.keyword_label_list = []
        for idx, keyword in enumerate(keywords):
            keyword_label = Label(self, text=keyword['keyword'], width=11, bg='#F4F6F8', relief='flat',
                                  borderwidth=4)
            self.keyword_label_list.append(keyword_label)
            keyword_label.bind("<Button-1>", lambda e, idx=idx: self.keyword_click(idx))
            if j % 3 == 0 and j > 0:
                i, j = i + 1, 0
            keyword_label.grid(row=i, column=j, sticky='e', pady=(2, 2), padx=(5, 5))
            j = j + 1
            self.keyword_idx_dict[keyword['keyword']] = idx

    def clean_keyword_label(self):
        for label in self.keyword_label_list:
            label.destroy()

    def get_selected_keyword(self):
        selected_keyword_ids = []
        for label in self.keyword_label_list:
            if label['bg'] == '#408CFB':
                selected_keyword_ids.append(self.keywords[self.keyword_idx_dict[label['text']]]['id'])
        return selected_keyword_ids


class NewContactFrame(Frame):
    def __init__(self, parent, app_type, app_type_comvalue, contact_list_frame, base_frame):
        super().__init__(parent, height=40, width=500, bg='white')
        self.app_type_comvalue = app_type_comvalue
        self.app_type = app_type
        self.base_frame = base_frame
        self.contact_list_frame = contact_list_frame
        new_contact_label = Label(self, width=10, text='用户或群', bg='white', anchor='w')
        new_contact_label.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(0, 0), fill='y')

        self.new_contact_entry = Entry(self, width=16, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.new_contact_entry.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(0, 0), fill='y')

        self.add_btn_image = ImageTk.PhotoImage(
            Image.open(Config.add_btn).resize((50, 23), Image.ANTIALIAS))
        new_contact_btn = Button(self, image=self.add_btn_image, bg='white', borderwidth=0,
                                 command=self.add_new_contact)
        new_contact_btn.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(0, 0), fill='y')

    def add_new_contact(self):
        current_app = self.app_type_comvalue.get()
        if len(self.new_contact_entry.get().strip()) == 0:
            return
        if not get_login_status(self.base_frame.setting_frame.parent):
            return
        data = {
            "appId": self.app_type[current_app],
            "contactName": self.new_contact_entry.get()
        }
        add_app_contact(data)
        contacts = get_rpa_contact(self.app_type[current_app])['data']
        self.contact_list_frame.update_contact(contacts, current_app)
        self.new_contact_entry.delete(0, END)


class NewKeywordFrame(Frame):
    def __init__(self, parent, keyword_list_frame, base_frame):
        super().__init__(parent, height=40, width=500, bg='white')
        self.keyword_list_frame = keyword_list_frame
        self.base_frame = base_frame
        new_keyword_label = Label(self, width=10, text='新的关键词', bg='white', anchor='w')
        new_keyword_label.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(0, 0), fill='y')

        self.new_keyword_entry = Entry(self, width=16, bg='#F4F6F8', relief='flat', borderwidth=4)
        self.new_keyword_entry.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(0, 0), fill='y')

        self.add_btn_image = ImageTk.PhotoImage(
            Image.open(Config.add_btn).resize((50, 23), Image.ANTIALIAS))
        new_keyword_btn = Button(self, image=self.add_btn_image, bg='white', borderwidth=0,
                                 command=self.add_new_contact)
        new_keyword_btn.pack(side=LEFT, anchor=NW, padx=(15, 0), pady=(0, 0), fill='y')

    def add_new_contact(self):
        if len(self.new_keyword_entry.get().strip()) == 0:
            return
        if not get_login_status(self.base_frame.setting_frame.parent):
            return
        data = {
            "keyword": self.new_keyword_entry.get()
        }
        add_app_keyword(data)
        keywords = get_keyword_list()['data']
        self.keyword_list_frame.update_keywords(keywords)
        self.new_keyword_entry.delete(0, END)


class ImageBrowserFrame(Frame):
    def __init__(self, parent, images=None):
        super().__init__(parent, bg='black')
        self.add_new_image_btn_image = ImageTk.PhotoImage(
            Image.open(Config.add_image_btn).resize((50, 50), Image.ANTIALIAS))
        add_new_image_btn = Button(self, width=50, height=50, image=self.add_new_image_btn_image, bg='white',
                                   relief='flat', borderwidth=0, command=self.browse_files)
        add_new_image_btn.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(0, 0), fill='both')
        self.delete_icon_image = ImageTk.PhotoImage(Image.open(Config.delete_icon).resize((10, 10), Image.ANTIALIAS))
        self.image_frame_dict = {}
        self.deleted_image = []
        self.deleted_image_url = []

        if images is not None:
            for filename in images:
                self.add_image_frame(filename)

    def browse_files(self):
        filename = filedialog.askopenfilename(initialdir="E:\Pictures", title="Select a File",
                                              filetypes=(("image", ".jpeg"), ("image", ".gif"), ("image", ".png"),
                                                         ("image", ".jpg")))
        self.add_image_frame(filename)

    def add_image_frame(self, filename):
        image_frame = ImageFrame(self, filename, 50, 50)
        image_frame.pack(side=LEFT, anchor=NW, padx=(0, 0), pady=(0, 0), fill='both')
        delete_icon_label = Button(self, image=self.delete_icon_image, relief='flat', borderwidth=0,
                                   command=lambda: self.delete_image(filename))
        image_frame.add(delete_icon_label, 40, 1)
        self.image_frame_dict[filename] = image_frame

    def delete_image(self, filename):
        self.image_frame_dict[filename].destroy()
        del self.image_frame_dict[filename]
        if is_url(filename):
            image_name = filename.split('imageName=')[-1]
            self.deleted_image.append(image_name)
            self.deleted_image_url.append(filename)

    def get_upload_images(self):
        all_images = list(self.image_frame_dict.keys())
        upload_images = []
        for i in all_images:
            if not is_url(i):
                upload_images.append(i)
        return upload_images

    def get_delete_images(self):
        return self.deleted_image


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class ImageFrame(Frame):
    def __init__(self, parent, file_path, width, height):
        super().__init__(parent, borderwidth=0, highlightthickness=0)

        self.canvas = Canvas(self, width=width, height=height)
        self.canvas.pack()

        if is_url(file_path):
            pil_img = get_image_by_url(file_path)
        else:
            pil_img = Image.open(file_path)
        self.img = ImageTk.PhotoImage(pil_img.resize((width, height), Image.ANTIALIAS))
        self.bg = self.canvas.create_image(0, 0, anchor=NW, image=self.img)

    def add(self, widget, x, y):
        self.canvas.create_window(x, y, anchor=NW, window=widget)
        return widget


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info'):
        self.waittime = 1  # miliseconds
        self.wraplength = 180  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.tw.attributes('-topmost', 'true')
        label = Label(self.tw, text=self.text, justify='left',
                      background="#ffffff", relief='solid', borderwidth=1,
                      wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class SplitLine(Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=0, highlightthickness=0)
        split_line = Frame(parent, height=1, relief=GROOVE, highlightthickness=1, highlightbackground="#F0F0F0",
                           highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, padx=(0, 0), pady=(0, 0), fill='x')
