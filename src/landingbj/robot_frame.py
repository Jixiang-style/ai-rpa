# cython: language_level=3
from tkinter import Frame, TOP, Label, NW, GROOVE, Button, SE, LEFT, END, FLAT, Text, INSERT

from PIL import ImageTk, Image

from landingbj.config import Config
from landingbj.gui_module import CreateToolTip
from landingbj.message_box import get_login_status
from landingbj.qa import delete_qa_detail, add_qa_detail, update_qa_detail


class QaFrame(Frame):
    def __init__(self, parent, height, width, data, setting_frame):
        super().__init__(parent)
        self.setting_frame = setting_frame
        self.parent = parent
        self.data = data

        self.qa_icon = ImageTk.PhotoImage(Image.open(Config.qa_icon).resize((20, 20), Image.ANTIALIAS))
        self.question_icon = ImageTk.PhotoImage(Image.open(Config.question_icon).resize((27, 27), Image.ANTIALIAS))
        self.answer_icon = ImageTk.PhotoImage(Image.open(Config.answer_icon).resize((27, 27), Image.ANTIALIAS))

        self.item_frame = Frame(parent, height=height, width=width, bg='white', borderwidth=1)
        self.item_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=10, padx=5)

        title_frame = Frame(self.item_frame, height=33, width=width, bg='white', borderwidth=1)
        qa_image_label = Label(title_frame, image=self.qa_icon, bg='white')
        qa_image_label.pack(side=LEFT, anchor=NW, fill='y', expand=True, pady=3, padx=5)

        self.update_btn_image = ImageTk.PhotoImage(Image.open(Config.update_btn).resize((50, 23), Image.ANTIALIAS))
        self.update_btn = Button(title_frame, image=self.update_btn_image, bg='white', borderwidth=0,
                                 command=lambda: self.show_update_frame(data['qid']))
        self.update_btn.pack(side=LEFT, anchor=NW, fill='y', pady=3, padx=(20, 0))

        self.delete_btn_image = ImageTk.PhotoImage(Image.open(Config.delete_btn).resize((50, 23), Image.ANTIALIAS))
        delete_btn = Button(title_frame, image=self.delete_btn_image, bg='white', borderwidth=0,
                            command=lambda: self.delete_qa_data(data['qid']))
        delete_btn.pack(side=LEFT, anchor=NW, fill='y', pady=3, padx=(20, 10))

        title_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=0)
        split_line = Frame(self.item_frame, height=1, relief=GROOVE,
                           highlightthickness=1, highlightbackground="#F0F0F0", highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=0)

        self.question_frame = Frame(self.item_frame, height=40, width=width, bg='white', borderwidth=1)
        question_image_label = Label(self.question_frame, image=self.question_icon, bg='white')
        question_image_label.pack(side=LEFT, anchor=NW, fill='y', pady=5, padx=(0, 10))
        self.question_text = Label(self.question_frame, bg='white', justify='left', height=1, anchor=NW, width=40,
                                   text=self.data['question'])
        self.question_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))
        self.question_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=5)

        split_line = Frame(self.item_frame, height=1, relief=GROOVE,
                           highlightthickness=1, highlightbackground="#F0F0F0", highlightcolor="#F0F0F0")
        split_line.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=0)

        self.answer_frame = Frame(self.item_frame, height=40, width=width, bg='white', borderwidth=1)

        answer_image_label = Label(self.answer_frame, image=self.answer_icon, bg='white')
        answer_image_label.pack(side=LEFT, anchor=NW, fill='y', pady=5, padx=(0, 10))

        self.answer_text = Label(self.answer_frame, bg='white', justify='left', height=1, anchor=NW, width=40,
                                 text=self.data['answer'])
        self.answer_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))
        self.answer_frame.pack(side=TOP, anchor=NW, fill='both', expand=True, pady=0, padx=5)

        CreateToolTip(self.question_text, self.question_text['text'])
        CreateToolTip(self.answer_text, self.answer_text['text'])

    def show_update_frame(self, qid):
        self.question_text.destroy()
        self.question_text = Text(self.question_frame, width=40, height=3, bg='#F4F6F8', bd=4, relief=FLAT)
        self.set_input(self.question_text, self.data['question'])
        self.question_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))

        self.answer_text.destroy()
        self.answer_text = Text(self.answer_frame, width=40, height=3, bg='#F4F6F8', bd=4, relief=FLAT)
        self.set_input(self.answer_text, self.data['answer'])
        self.answer_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))

        self.confirm_btn_image = ImageTk.PhotoImage(Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))
        self.update_btn['image'] = self.confirm_btn_image
        self.update_btn['command'] = lambda: self.update_qa_detail(self.data['qid'])

    def reset(self):
        self.question_text.destroy()
        self.question_text = Label(self.question_frame, bg='white', justify='left', height=1, anchor=NW, width=40,
                                   text=self.data['question'])
        self.question_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))
        self.answer_text.destroy()
        self.answer_text = Label(self.answer_frame, bg='white', justify='left', height=1, anchor=NW, width=40,
                                 text=self.data['answer'])
        self.answer_text.pack(side=LEFT, anchor=NW, fill='x', pady=(10, 10), padx=(5, 10))

        self.update_btn['image'] = self.update_btn_image
        self.update_btn['command'] = lambda: self.show_update_frame(self.data['qid'])

    def delete_qa_data(self, qid):
        if not get_login_status(self.setting_frame.parent):
            return

        result = delete_qa_detail(qid)
        if result['status'] == 'success':
            self.setting_frame.reset_qa_list_frame()

    def update_qa_detail(self, qid):
        if not get_login_status(self.setting_frame.parent):
            self.reset()
            return

        q = self.question_text.get("1.0", END).strip()
        a = self.answer_text.get("1.0", END).strip()

        if len(q) == 0:
            self.question_text.focus()
            return

        if len(a) == 0:
            self.answer_text.focus()
            return

        data = {
            "question": q,
            "answer": a,
            "qid": qid,
            "category": Config.channel_name
        }
        result = update_qa_detail(data)
        if len(result) > 0:
            self.data['question'], self.data['answer'] = q, a
        self.reset()

    def set_input(self, text, value):
        text.delete(1.0, END)
        text.insert(END, value.strip())
        if text.get('end-1c', END) == '\n':
            text.delete('end-1c', END)


class QaAddOrUpdateFrame(Frame):
    def __init__(self, parent, setting_frame, data=None):
        super().__init__(parent)
        self.setting_frame = setting_frame
        self.parent = parent
        self.data = data

        self.question_icon = ImageTk.PhotoImage(Image.open(Config.question_icon).resize((27, 27), Image.ANTIALIAS))
        self.answer_icon = ImageTk.PhotoImage(Image.open(Config.answer_icon).resize((27, 27), Image.ANTIALIAS))

        question_frame = Frame(self.parent, height=130, width=100, bg='white', borderwidth=1)
        question_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(10, 10), fill='x')

        question_image_label = Label(question_frame, image=self.question_icon, bg='white')
        question_image_label.pack()
        question_image_label.place(relx=0.05, y=7)

        question_label = Label(question_frame, text='问题', bg='white')
        question_label.pack()
        question_label.place(relx=0.15, y=10)

        self.entry_question_input = Text(question_frame, fg='#7B7B7B', bg='#F4F6F8', width=20, height=3, borderwidth=0)
        self.entry_question_input.pack()
        self.entry_question_input.place(relx=0.05, y=46, relwidth=0.9, height=70)

        answer_frame = Frame(self.parent, height=130, width=100, bg='white', borderwidth=1)
        answer_frame.pack(side=TOP, anchor=NW, padx=(10, 10), pady=(0, 10), fill='x')

        answer_image_label = Label(answer_frame, image=self.answer_icon, bg='white')
        answer_image_label.pack()
        answer_image_label.place(relx=0.05, y=7)

        answer_label = Label(answer_frame, text='答案', bg='white')
        answer_label.pack()
        answer_label.place(relx=0.15, y=10)

        self.entry_answer_input = Text(answer_frame, fg='#7B7B7B', bg='#F4F6F8', width=20, height=3, borderwidth=0)
        self.entry_answer_input.pack()
        self.entry_answer_input.place(relx=0.05, y=46, relwidth=0.9, height=70)

        btn_frame = Frame(self.parent, height=25, borderwidth=1)
        btn_frame.pack(side=TOP, anchor=NW, padx=0, pady=(0, 10), fill='both')

        self.confirm_btn_image = ImageTk.PhotoImage(
            Image.open(Config.confirm_btn).resize((50, 23), Image.ANTIALIAS))
        confirm_btn = Button(btn_frame, image=self.confirm_btn_image, borderwidth=0)
        confirm_btn.pack()
        confirm_btn.place(height=23, width=50, anchor=SE, relx=0.7, rely=1)
        self.cancel_btn_image = ImageTk.PhotoImage(
            Image.open(Config.cancel_btn).resize((50, 23), Image.ANTIALIAS))
        self.cancel_btn = Button(btn_frame, image=self.cancel_btn_image, borderwidth=0,
                                 command=lambda: self.reset_qa_list())
        self.cancel_btn.pack()
        self.cancel_btn.place(height=23, width=50, anchor=SE, relx=0.9, rely=1)

        if self.data is None:
            confirm_btn['command'] = lambda: self.add_qa_detail()
        else:
            self.entry_question_input.insert(INSERT, self.data['question'])
            self.entry_answer_input.insert(INSERT, self.data['answer'])
            confirm_btn['command'] = lambda: self.update_qa_detail(self.data['qid'])

    def reset_qa_list(self):
        self.setting_frame.reset_qa_list_frame()

    def add_qa_detail(self):
        if not get_login_status(self.setting_frame.parent):
            return

        q = self.entry_question_input.get("1.0", END).strip()
        a = self.entry_answer_input.get("1.0", END).strip()

        if len(q) == 0:
            self.entry_question_input.focus()
            return

        if len(a) == 0:
            self.entry_answer_input.focus()
            return

        data = {
            "question": self.entry_question_input.get("1.0", END),
            "answer": self.entry_answer_input.get("1.0", END),
            "qid": "-1",
            "category": Config.channel_name
        }
        add_qa_detail(data)
        self.reset_qa_list()
