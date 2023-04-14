# cython: language_level=3
import io
from tkinter import Frame, Label, Button, LEFT, ttk, Entry, END, Text, W, TOP, BOTH

from PIL import ImageTk, Image
from ttkthemes import ThemedStyle

from landingbj.config import Config
from landingbj.contact_frame import ContactFrame
from landingbj.gui_module import ScrollFrame, GuiCache
from landingbj.message_box import get_login_status
from landingbj.qa import get_qa_list, get_timer_list, get_repeater_list
from landingbj.repeater_frame import RepeaterAddOrUpdateFrame, RepeaterFrame
from landingbj.robot_frame import QaAddOrUpdateFrame, QaFrame
from landingbj.timer_frame import TimerAddOrUpdateFrame, TimerFrame
from landingbj.util import get_tk_icon
from landingbj.qa import get_image_from_sd

# ROBOT_TAB_NAME = '机器人'
# TIMER_TAB_NAME = '定时器'
# REPEATER_TAB_NAME = '烽火台'
# CONTACT_TAB_NAME = '联系人'
ROBOT_TAB_NAME = '文本生成'
TIMER_TAB_NAME = '图片生成'
REPEATER_TAB_NAME = '协调联动'
CONTACT_TAB_NAME = '联系人'

TAB_NAME_ID_DICT = {
    ROBOT_TAB_NAME: 0,
    TIMER_TAB_NAME: 1,
    REPEATER_TAB_NAME: 2,
}


class SettingTabFrame(Frame):
    def __init__(self, parent, height, width, main_frame):
        super().__init__(parent, bg='#F0F0F0')
        style = ThemedStyle(self)
        style.set_theme("arc")
        style.configure("TNotebook", background='#F0F0F0')
        if Config.scale_ratio == 1:
            style.configure("TNotebook.Tab", padding=(17, 2))
        elif Config.scale_ratio == 1.25:
            style.configure("TNotebook.Tab", padding=(28, 2))
        else:
            style.configure("TNotebook.Tab", padding=(39, 2))

        style.configure("TCombobox", troughcolor='white', background='white', lightcolor='white', foreground='black',
                        selectforeground='black', darkcolor='white', selectbackground='white', side='right')
        self.parent = parent
        self.main_frame = main_frame
        self.height = height
        self.width = width

        self.tab_control = ttk.Notebook(self)
        self.robot_frame = ttk.Frame(self.tab_control)
        self.timer_frame = ttk.Frame(self.tab_control)
        self.repeater_frame = ttk.Frame(self.tab_control)
        self.contact_frame = ttk.Frame(self.tab_control)

        self.tab_control.add(self.robot_frame, text=ROBOT_TAB_NAME)
        self.tab_control.add(self.timer_frame, text=TIMER_TAB_NAME)
        self.tab_control.add(self.repeater_frame, text=REPEATER_TAB_NAME)
        self.tab_control.add(self.contact_frame, text=CONTACT_TAB_NAME)
        self.tab_control.pack(expand=1, fill="both", pady=(5, 0))

        self.robot_icon = get_tk_icon(Config.robot_icon, (23, 23))
        self.app_type_label = Label(self, image=self.robot_icon, borderwidth=0, height=25, width=25)
        self.app_type_label.pack()
        self.app_type_label.place(relx=0.76, y=5)
        self.current_tab = ROBOT_TAB_NAME

        self.cross_bar_icon = get_tk_icon(Config.cross_bar_icon, (20, 20))
        self.add_data_btn = Button(self, image=self.cross_bar_icon, borderwidth=0, height=25,
                                   width=25, command=lambda: self.add_data())
        self.add_data_btn.pack()
        self.add_data_btn.place(relx=0.90, y=5)
        # self.tab_control.bind("<<NotebookTabChanged>>", self.tab_on_change)
        self.tab_control.bind("<ButtonRelease-1>", self.remove_focus_state)
        self.qa_data_page = 1
        self.qa_data_page_size = 5
        self.main_frame.change_switch_bg(ROBOT_TAB_NAME)

        self.contact_icon = get_tk_icon(Config.add_contact_icon, (20, 20))
        self.contact_return_icon = get_tk_icon(Config.contact_return_icon, (20, 20))
        self.contact_icon_btn = Button(self, image=self.contact_icon, borderwidth=0, height=25,
                                       width=25, command=lambda: self.show_contact_tab())
        self.contact_icon_btn.pack()
        self.contact_icon_btn.place(relx=0.83, y=5)

        self.tab_control.hide(3)
        # self.tab_control.pack(expand=1, fill="both", pady=(5, 0))

        self.reset_qa_list_frame()
        self.contact_frame_status = False

        # self.tab_control.select(2)
        # self.add_data()
        # self.reset_timer_list_frame()
        # self.show_timer_update_frame(25)
        # self.show_contact_tab()

    def show_contact_tab(self):
        tab_id = TAB_NAME_ID_DICT[self.current_tab]
        if self.current_tab == ROBOT_TAB_NAME:
            self.tab_control.insert(tab_id, self.contact_frame, text=CONTACT_TAB_NAME)
            self.tab_control.add(self.contact_frame, text=ROBOT_TAB_NAME)
        elif self.current_tab == TIMER_TAB_NAME:
            self.tab_control.insert(tab_id, self.contact_frame, text=CONTACT_TAB_NAME)
            self.tab_control.add(self.contact_frame, text=TIMER_TAB_NAME)
        elif self.current_tab == REPEATER_TAB_NAME:
            self.tab_control.insert(tab_id, self.contact_frame, text=CONTACT_TAB_NAME)
            self.tab_control.add(self.contact_frame, text=REPEATER_TAB_NAME)
        self.tab_control.hide(tab_id + 1)
        self.tab_control.select(tab_id)
        self.tab_on_change(CONTACT_TAB_NAME)
        self.contact_icon_btn['image'] = self.contact_return_icon
        self.contact_icon_btn['command'] = lambda: self.hide_contact_tab()
        self.contact_frame_status = True

    def hide_contact_tab(self, select_tab=None):
        tab_id = TAB_NAME_ID_DICT[self.current_tab]
        if self.current_tab == ROBOT_TAB_NAME:
            self.tab_control.insert(self.contact_frame, self.robot_frame, text=ROBOT_TAB_NAME)
            self.tab_control.add(self.robot_frame, text=ROBOT_TAB_NAME)
        elif self.current_tab == TIMER_TAB_NAME:
            self.tab_control.insert(self.contact_frame, self.timer_frame, text=TIMER_TAB_NAME)
            self.tab_control.add(self.timer_frame, text=TIMER_TAB_NAME)
        elif self.current_tab == REPEATER_TAB_NAME:
            self.tab_control.insert(self.contact_frame, self.repeater_frame, text=REPEATER_TAB_NAME)
            self.tab_control.add(self.repeater_frame, text=REPEATER_TAB_NAME)
        self.tab_control.hide(tab_id + 1)

        if select_tab is None:
            self.tab_control.select(tab_id)
        self.refresh_current_tab()
        self.contact_icon_btn['image'] = self.contact_icon
        self.contact_icon_btn['command'] = lambda: self.show_contact_tab()
        self.contact_frame_status = False

    def remove_focus_state(self, event):
        self.tab_control.state(["!focus"])
        if self.contact_frame_status:
            choice = self.tab_control.tab(self.tab_control.select(), "text")
            if choice != self.current_tab:
                self.hide_contact_tab(TAB_NAME_ID_DICT[choice])
            else:
                self.hide_contact_tab()
        else:
            self.refresh_current_tab()

    def refresh_current_tab(self):
        choice = self.tab_control.tab(self.tab_control.select(), "text")
        self.tab_on_change(choice)

    def tab_on_change(self, choice):
        if choice == ROBOT_TAB_NAME:
            # self.reset_qa_list_frame()
            # 文本生成
            # 创建子容器
            robot_input_frame = Frame(self.robot_frame)
            robot_input_frame.pack(side=TOP, fill=BOTH)
            robot_text_frame = Frame(self.robot_frame)
            robot_text_frame.pack(side=TOP, fill=BOTH)
            robot_output_frame = Frame(self.robot_frame)
            robot_output_frame.pack()

            input_frame = Frame(robot_input_frame)
            input_frame.pack(side=TOP, fill=BOTH, padx=5, pady=5)

            input_text = Entry(input_frame)
            input_text.pack(side=LEFT)

            # 创建"处理"按钮
            def handle_text():
                text = query_text()
                # input_text.delete(0, END)
                resulet_text.delete("1.0", END)
                resulet_text.insert(END, text + "\n")

            # todo 待调FastChat接口
            def query_text():
                text = input_text.get()
                print(text)
                return "123456"

            # todo "处理"按钮换成图标。布局样式待调整
            process_button = Button(input_frame, text="处理", command=handle_text)
            process_button.pack(side=LEFT, fill=BOTH, padx=5, pady=5)

            # 创建结果文本框
            result_label = Label(robot_text_frame, text="文本结果：", anchor=W)
            result_label.pack(side=TOP, anchor=W)
            result_frame = Frame(robot_output_frame)
            result_frame.pack(expand=True, padx=5, pady=5)
            resulet_text = Text(result_frame)
            resulet_text.pack(side=TOP, fill=BOTH, expand=True)

            self.robot_icon = get_tk_icon(Config.robot_icon, (23, 23))
            self.app_type_label['image'] = self.robot_icon
            self.current_tab = ROBOT_TAB_NAME
        elif choice == TIMER_TAB_NAME:
            # self.reset_timer_list_frame()
            # 图片生成
            timer_input_frame = Frame(self.timer_frame)
            timer_input_frame.pack(side=TOP, fill=BOTH)
            timer_text_frame = Frame(self.timer_frame)
            timer_text_frame.pack(side=TOP, fill=BOTH)
            timer_output_frame = Frame(self.timer_frame)
            timer_output_frame.pack()

            input_frame = Frame(timer_input_frame)
            input_frame.pack(side=TOP, fill=BOTH, padx=5, pady=5)

            input_text = Entry(input_frame)
            input_text.pack(side=LEFT)

            # 创建"处理"按钮
            def handle_image():
                context = query_content()
                # input_text.delete(0, END)
                resulet_text.delete("1.0", END)
                resulet_text.insert(END, context)
                return resulet_text

            # 调ai接口
            def query_content():
                text = input_text.get()
                content = get_image_from_sd(str(text))
                print(f"响应的结果类型：{type(content)} \n  类型：{content}")
                if isinstance(type(content), bytes):
                    # 处理传递过来的图片字节流（todo 处理方式待改进，前端无法展示图片）
                    image = Image.open(io.BytesIO(content))
                    photo_image = ImageTk.PhotoImage(image)
                    # 清除image对象，释放内存
                    image.close()
                    return photo_image
                return TypeError("返回数据类型有误")

            # todo "处理"按钮换成图标。布局样式待调整
            process_button = Button(input_frame, text="处理", command=handle_image)
            process_button.pack(side=LEFT, fill=BOTH, padx=5, pady=5)

            # 创建结果文本框
            result_label = Label(timer_text_frame, text="图片结果：", anchor=W)
            result_label.pack(side=TOP, anchor=W)
            result_frame = Frame(timer_output_frame)
            result_frame.pack(expand=True, padx=5, pady=5)
            resulet_text = Text(result_frame)
            resulet_text.pack(side=TOP, fill=BOTH, expand=True)

            self.timer_icon = get_tk_icon(Config.timer_icon, (23, 23))
            self.app_type_label['image'] = self.timer_icon
            self.current_tab = TIMER_TAB_NAME
        elif choice == REPEATER_TAB_NAME:
            # todo 协调联动 页面待完成
            self.reset_repeater_list_frame()
            self.monitor_icon = get_tk_icon(Config.monitor_icon, (23, 23))
            self.app_type_label['image'] = self.monitor_icon
            self.current_tab = REPEATER_TAB_NAME
        else:
            self.reset_contact_frame()
        self.main_frame.change_switch_bg(choice)

    def reset_setting_detail_frame(self, frame):
        if hasattr(self, 'scroll_frame'):
            self.scroll_frame.destroy()
        self.init_setting_detail_frame(frame)

    def add_data(self):
        if self.contact_frame_status:
            return
        tab_name = self.tab_control.tab(self.tab_control.select(), "text")
        if tab_name == ROBOT_TAB_NAME:
            self.reset_setting_detail_frame(self.robot_frame)
            QaAddOrUpdateFrame(self.setting_detail_frame, self)

        elif tab_name == TIMER_TAB_NAME:
            self.reset_setting_detail_frame(self.timer_frame)
            TimerAddOrUpdateFrame(self.setting_detail_frame, self)

        elif tab_name == REPEATER_TAB_NAME:
            self.reset_setting_detail_frame(self.repeater_frame)
            RepeaterAddOrUpdateFrame(self.setting_detail_frame, self)

    def show_qa_update_frame(self, qid):
        self.reset_setting_detail_frame(self.robot_frame)
        QaAddOrUpdateFrame(self.setting_detail_frame, self, GuiCache.qa_data_cache[qid])

    def show_timer_update_frame(self, data_id):
        self.reset_setting_detail_frame(self.timer_frame)
        TimerAddOrUpdateFrame(self.setting_detail_frame, self, GuiCache.timer_data_cache[data_id])

    def show_repeater_update_frame(self, data_id):
        self.reset_setting_detail_frame(self.repeater_frame)
        RepeaterAddOrUpdateFrame(self.setting_detail_frame, self, GuiCache.repeater_data_cache[data_id])

    def init_setting_detail_frame(self, frame):
        tab_name = self.tab_control.tab(self.tab_control.select(), "text")
        if tab_name == ROBOT_TAB_NAME:
            self.scroll_frame = ScrollFrame(frame, self)
        else:
            self.scroll_frame = ScrollFrame(frame)
        self.scroll_frame.pack(side=LEFT, padx=0, pady=0, fill='both', expand=True)
        self.setting_detail_frame = Frame(self.scroll_frame.viewPort, height=self.height - 50,
                                          width=self.width, borderwidth=0)
        self.setting_detail_frame.pack(side=LEFT, padx=0, pady=0, fill='both', expand=True)

    def update_qa_list_frame(self):
        if self.contact_frame_status:
            return
        self.qa_data_page = self.qa_data_page + 1
        self.qa_data = get_qa_list(self.qa_data_page, self.qa_data_page_size)
        for item in self.qa_data['list']:
            QaFrame(self.setting_detail_frame, Config.robot_frame_height, self.width, item, self)
            GuiCache.qa_data_cache[item['qid']] = item

    def reset_qa_list_frame(self):
        self.reset_setting_detail_frame(self.robot_frame)
        self.qa_data_page, self.qa_data_page_size = 1, 5
        self.qa_data = get_qa_list(self.qa_data_page, self.qa_data_page_size)
        GuiCache.qa_data_cache = {}
        if self.qa_data is None:
            return
        for item in self.qa_data['list']:
            QaFrame(self.setting_detail_frame, Config.robot_frame_height, self.width, item, self)
            GuiCache.qa_data_cache[item['qid']] = item

    def reset_timer_list_frame(self):
        self.reset_setting_detail_frame(self.timer_frame)
        self.timer_data = get_timer_list()
        GuiCache.timer_data_cache = {}
        if self.timer_data is None:
            return
        for item in self.timer_data['data']:
            TimerFrame(self.setting_detail_frame, Config.robot_frame_height, self.width, item, self)
            GuiCache.timer_data_cache[item['id']] = item

    def reset_repeater_list_frame(self):
        self.reset_setting_detail_frame(self.repeater_frame)
        self.repeater_data = get_repeater_list()
        GuiCache.repeater_data_cache = {}
        if self.repeater_data is None:
            return
        for item in self.repeater_data['data']:
            RepeaterFrame(self.setting_detail_frame, Config.qa_frame_height, self.width, item, self)
            GuiCache.repeater_data_cache[item['id']] = item

    def reset_contact_frame(self):
        if not get_login_status(self.parent):
            return
        self.reset_setting_detail_frame(self.contact_frame)
        ContactFrame(self.setting_detail_frame, self.parent)
