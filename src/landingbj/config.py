#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# config.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#

# cython: language_level=3
import os
import random
import sys

from ai.config import AiConfig
import tempfile


def resource_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./resource")

    return base_path + '/'


class Config:
    image_app_dir = resource_path() + 'app/'
    image_gui_dir = resource_path() + 'gui/'

    image_app_dir_wechat = image_app_dir + 'wechat/default/'
    image_app_dir_qq = image_app_dir + 'qq/default/'
    image_app_dir_ding = image_app_dir + 'ding5/default/'
    image_app_dir_weibo = image_app_dir + 'weibo/default/'
    image_app_dir_momo = image_app_dir + 'momo/default/'
    image_app_dir_ding6 = image_app_dir + 'ding6/default/'
    image_app_dir_51job = image_app_dir + '51job/default/'
    image_app_dir_whatsapp = image_app_dir + 'whatsapp/default/'
    image_app_dir_line = image_app_dir + 'line/default/'
    image_app_dir_tiktok = image_app_dir + 'tiktok/'
    image_app_dir_kuaishou = image_app_dir + 'kuaishou/'

    if sys.platform == "darwin":
        screenshot = tempfile.gettempdir() + '/screenshot.png'
        cube_logo = image_gui_dir + 'cube.gif'
        wand_edge_image = image_gui_dir + 'image_wand_edge.gif'
        ding_copy = image_gui_dir + 'ding_copy.gif'
        pos_icon = image_gui_dir + 'pos.gif'
        start_icon = image_gui_dir + 'start.gif'
        continue_icon = image_gui_dir + 'continue.gif'
        stop_icon = image_gui_dir + 'stop.gif'
        save_icon = image_gui_dir + 'save.gif'
        retry_icon = image_gui_dir + 'retry.gif'
        reset_icon = image_gui_dir + 'reset.gif'
    else:
        screenshot = tempfile.gettempdir() + '/screenshot.png'
        cube_logo = image_gui_dir + 'cube.png'
        wand_edge_image = image_gui_dir + 'image_wand_edge.png'
        ding_copy = image_gui_dir + 'ding_copy.png'
        pos_icon = image_gui_dir + 'pos.png'
        pos_icon_gray = image_gui_dir + 'pos_gray.png'
        start_icon = image_gui_dir + 'start.png'
        continue_icon = image_gui_dir + 'continue.png'
        stop_icon = image_gui_dir + 'stop.png'
        save_icon = image_gui_dir + 'save.png'
        retry_icon = image_gui_dir + 'retry.png'
        reset_icon = image_gui_dir + 'reset.png'
        setting_icon = image_gui_dir + 'setting.png'
        cross_bar_icon = image_gui_dir + 'cross_bar.png'
        add_contact_icon = image_gui_dir + 'add_contact_icon.png'
        qa_icon = image_gui_dir + 'qa_icon.png'
        question_icon = image_gui_dir + 'question_icon.png'
        answer_icon = image_gui_dir + 'answer_icon.png'
        time_icon = image_gui_dir + 'time_icon.png'
        timer_placeholder = image_gui_dir + 'timer_placeholder.png'
        contact_icon = image_gui_dir + 'contact_icon.png'
        add_image_btn = image_gui_dir + 'add_image_btn.png'
        delete_icon = image_gui_dir + 'delete_icon.png'
        arrow_icon = image_gui_dir + 'arrow_icon.png'
        confirm_btn = image_gui_dir + 'confirm_btn.png'
        cancel_btn = image_gui_dir + 'cancel_btn.png'
        update_btn = image_gui_dir + 'update_btn.png'
        delete_btn = image_gui_dir + 'delete_btn.png'
        add_btn = image_gui_dir + 'add_btn.png'
        robot_icon = image_gui_dir + 'robot_icon.png'
        timer_icon = image_gui_dir + 'timer_icon.png'
        monitor_icon = image_gui_dir + 'monitor_icon.png'
        contact_return_icon = image_gui_dir + 'contact_return_icon.png'
        expand_icon = image_gui_dir + 'expand_icon.png'
        shrink_icon = image_gui_dir + 'shrink_icon.png'
        delete_contact_icon = image_gui_dir + 'delete_contact_icon.png'
        save_contact_icon = image_gui_dir + 'save_contact_icon.png'
        update_contact_icon = image_gui_dir + 'update_contact_icon.png'
        contact_advance_icon = image_gui_dir + 'contact_advance.png'
        contact_start_icon = image_gui_dir + 'contact_start.png'
        contact_stop_icon = image_gui_dir + 'contact_stop.png'
        contact_pos_icon = image_gui_dir + 'contact_pos.png'
        contact_reset_icon = image_gui_dir + 'contact_reset.png'
        contact_commit_icon = image_gui_dir + 'contact_commit.png'

    round_logo_size = 30
    logo_offset_x = 64
    logo_offset_y = 10
    copy_offset_x = 25
    copy_offset_y = 25
    dial_region_ratio = 0.4
    app_area_duplicate_ration = 0.25
    search_contact_count = 3
    search_contact_interval = 1
    image_binarize_threshold = 202
    dymatic_binarize_threshold = 202
    qq_search_threshold = 0.9
    dial_wait_time = 20
    timer_wait_time = 1
    max_timer_wait_time = 32
    contact_wait_time = 60 * 10
    send_button_offset_left = 64
    send_button_offset_up = 16

    if sys.platform == 'win32':
        import win32gui
        import win32con
        windows_cursor_normal = win32gui.LoadCursor(win32con.NULL, win32con.IDC_ARROW)
        windows_cursor_text = win32gui.LoadCursor(win32con.NULL, win32con.IDC_IBEAM)
        window_cursor_link = win32gui.LoadCursor(win32con.NULL, win32con.IDC_HAND)
    mouse_cursor_normal = 0
    mouse_cursor_text = 1
    mouse_cursor_link = 2

    if sys.platform == "darwin":
        rpa_icon_robot = image_gui_dir + 'robot.gif'
        rpa_icon_timer = image_gui_dir + 'timer.gif'
        rpa_icon_monitor = image_gui_dir + 'monitor.gif'
        rpa_switch_on = image_gui_dir + 'rpa_switch_on.gif'
        rpa_switch_off = image_gui_dir + 'rpa_switch_off.gif'
        finger_icon = image_gui_dir + 'finger.gif'
        dial_button_icons = [
            [image_app_dir_wechat + 'wechat_100.gif', image_app_dir_qq + 'qq_100.gif', image_app_dir_ding + 'ding_100.gif',
             image_app_dir_wechat + 'wechat_gray_100.gif', image_app_dir_qq + 'qq_full_100.gif',
             image_app_dir_ding + 'ding_gray_100.gif',
             image_app_dir_ding + 'ding_full_100.gif', image_app_dir_weibo + 'weibo.gif', image_app_dir_momo + 'momo_100.gif',
             image_app_dir_ding6 + 'ding6_100.gif'],
            [image_app_dir_wechat + 'wechat_125.gif', image_app_dir_qq + 'qq_125.gif', image_app_dir_ding + 'ding_125.gif',
             image_app_dir_wechat + 'wechat_gray_125.gif', image_app_dir_qq + 'qq_full_125.gif',
             image_app_dir_ding + 'ding_gray_125.gif',
             image_app_dir_ding + 'ding_full_125.gif', image_app_dir_weibo + 'weibo.gif', image_app_dir_momo + 'momo.gif',
             image_app_dir_ding6 + 'ding6_125.gif'],
            [image_app_dir_wechat + 'wechat_150.gif', image_app_dir_qq + 'qq_150.gif', image_gui_dir + 'ding_150.gif',
             image_app_dir_wechat + 'wechat_gray_150.gif', image_app_dir_qq + 'qq_full_150.gif',
             image_app_dir_ding + 'ding_gray_150.gif',
             image_app_dir_ding + 'ding_full_150.gif', image_app_dir_weibo + 'weibo.gif', image_app_dir_momo + 'momo.gif',
             image_app_dir_ding6 + 'ding6_150.gif']
        ]
        no_contact_icons = [
            ['', '', image_app_dir_ding + 'ding_no_contact_100.gif', '', '',
             image_app_dir_ding + 'ding_no_contact_100.gif', image_app_dir_ding + 'ding_no_contact_100.gif',
             image_app_dir_weibo + 'weibo_no_contact_100.gif', image_app_dir_momo + 'momo_no_contact_100.gif'],
            ['', '', image_app_dir_ding + 'ding_no_contact_125.gif', '', '',
             image_app_dir_ding + 'ding_no_contact_125.gif', image_app_dir_ding + 'ding_no_contact_125.gif',
             image_app_dir_weibo + 'weibo_no_contact_125.gif', image_app_dir_momo + 'momo_no_contact_125.gif'],
            ['', '', image_app_dir_ding + 'ding_no_contact_150.gif', '', '',
             image_app_dir_ding + 'ding_no_contact_150.gif', image_app_dir_ding + 'ding_no_contact_150.gif',
             image_app_dir_weibo + 'weibo_no_contact_150.gif', image_app_dir_momo + 'momo_no_contact_150.gif']
        ]
        yes_contact_icons = [
            [image_app_dir_wechat + 'wechat_yes_contact_100.gif', image_app_dir_qq + 'qq_yes_contact_100.gif',
             '', image_app_dir_wechat + 'wechat_yes_contact_100.gif', image_app_dir_qq + 'qq_yes_contact_100.gif',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_100.gif'],
            [image_app_dir_wechat + 'wechat_yes_contact_125.gif', image_app_dir_qq + 'qq_yes_contact_125.gif',
             '', image_app_dir_wechat + 'wechat_yes_contact_125.gif', image_app_dir_qq + 'qq_yes_contact_125.gif',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_125.gif'],
            [image_app_dir_wechat + 'wechat_yes_contact_150.gif', image_app_dir_qq + 'qq_yes_contact_150.gif',
             '', image_app_dir_wechat + 'wechat_yes_contact_150.gif', image_app_dir_qq + 'qq_yes_contact_150.gif',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_150.gif']
        ]
        yes_group_icons = [
            [image_app_dir_wechat + 'wechat_yes_group_100.gif', image_app_dir_qq + 'qq_yes_group_100.gif',
             '', image_app_dir_wechat + 'wechat_yes_group_100.gif', image_app_dir_qq + 'qq_yes_group_100.gif'],
            [image_app_dir_wechat + 'wechat_yes_group_125.gif', image_app_dir_qq + 'qq_yes_group_125.gif',
             '', image_app_dir_wechat + 'wechat_yes_group_125.gif', image_app_dir_qq + 'qq_yes_group_125.gif'],
            [image_app_dir_wechat + 'wechat_yes_group_150.gif', image_app_dir_qq + 'qq_yes_group_150.gif',
             '', image_app_dir_wechat + 'wechat_yes_group_150.gif', image_app_dir_qq + 'qq_yes_group_150.gif']
        ]
        ding6_copy = [image_app_dir_ding6 + 'ding6_copy_100.gif', image_app_dir_ding6 + 'ding6_copy_125.gif',
                      image_app_dir_ding6 + 'ding6_copy_150.gif']

        ding6_contact_prompt = [image_app_dir_ding6 + 'ding_contact_100.gif', image_app_dir_ding6 + 'ding_contact_125.gif',
                                image_app_dir_ding6 + 'ding_contact_150.gif']

        weibo_send_image_button = image_app_dir_weibo + 'weibo_send_image_button.gif'
    else:
        rpa_icon_robot = image_gui_dir + 'robot.png'
        rpa_icon_timer = image_gui_dir + 'timer.png'
        rpa_icon_monitor = image_gui_dir + 'monitor.png'
        rpa_icon_robot_gray = image_gui_dir + 'robot_gray.png'
        rpa_icon_timer_gray = image_gui_dir + 'timer_gray.png'
        rpa_icon_monitor_gray = image_gui_dir + 'monitor_gray.png'
        rpa_switch_on = image_gui_dir + 'rpa_switch_on.png'
        rpa_switch_off = image_gui_dir + 'rpa_switch_off.png'
        finger_icon = image_gui_dir + 'finger.png'
        dial_button_icons = [
            [image_app_dir_wechat + 'wechat_100.png', image_app_dir_qq + 'qq_100.png', image_app_dir_ding + 'ding_100.png',
             image_app_dir_wechat + 'wechat_gray_100.png', image_app_dir_qq + 'qq_full_100.png',
             image_app_dir_ding + 'ding_gray_100.png',
             image_app_dir_ding + 'ding_full_100.png', image_app_dir_weibo + 'weibo.png', image_app_dir_momo + 'momo_100.png',
             image_app_dir_ding6 + 'ding6_100.png', image_app_dir_51job + '51job.png', image_app_dir_whatsapp + 'whatsapp_100.png',
             image_app_dir_line + 'line_100.png'],
            [image_app_dir_wechat + 'wechat_125.png', image_app_dir_qq + 'qq_125.png', image_app_dir_ding + 'ding_125.png',
             image_app_dir_wechat + 'wechat_gray_125.png', image_app_dir_qq + 'qq_full_125.png',
             image_app_dir_ding + 'ding_gray_125.png',
             image_app_dir_ding + 'ding_full_125.png', image_app_dir_weibo + 'weibo.png', image_app_dir_momo + 'momo.png',
             image_app_dir_ding6 + 'ding6_125.png', image_app_dir_51job + '51job.png', image_app_dir_whatsapp + 'whatsapp_125.png',
             image_app_dir_line + 'line_125.png'],
            [image_app_dir_wechat + 'wechat_150.png', image_app_dir_qq + 'qq_150.png', image_app_dir_ding + 'ding_150.png',
             image_app_dir_wechat + 'wechat_gray_150.png', image_app_dir_qq + 'qq_full_150.png',
             image_app_dir_ding + 'ding_gray_150.png',
             image_app_dir_ding + 'ding_full_150.png', image_app_dir_weibo + 'weibo.png', image_app_dir_momo + 'momo.png',
             image_app_dir_ding6 + 'ding6_150.png', image_app_dir_51job + '51job.png', image_app_dir_whatsapp + 'whatsapp_150.png',
             image_app_dir_line + 'line_150.png']
        ]
        no_contact_icons = [
            ['', '', image_app_dir_ding + 'ding_no_contact_100.png', '', '',
             image_app_dir_ding + 'ding_no_contact_100.png', image_app_dir_ding + 'ding_no_contact_100.png',
             image_app_dir_weibo + 'weibo_no_contact_100.png', '', '', '', image_app_dir_whatsapp + 'whatsapp_no_contact_100.png'],
            ['', '', image_app_dir_ding + 'ding_no_contact_125.png', '', '',
             image_app_dir_ding + 'ding_no_contact_125.png', image_app_dir_ding + 'ding_no_contact_125.png',
             image_app_dir_weibo + 'weibo_no_contact_125.png', '', '', '', image_app_dir_whatsapp + 'whatsapp_no_contact_125.png'],
            ['', '', image_app_dir_ding + 'ding_no_contact_150.png', '', '',
             image_app_dir_ding + 'ding_no_contact_150.png', image_app_dir_ding + 'ding_no_contact_150.png',
             image_app_dir_weibo + 'weibo_no_contact_150.png', '', '', '', image_app_dir_whatsapp + 'whatsapp_no_contact_150.png']
        ]
        yes_contact_icons = [
            [image_app_dir_wechat + 'wechat_yes_contact_100.png', image_app_dir_qq + 'qq_yes_contact_100.png',
             '', image_app_dir_wechat + 'wechat_yes_contact_100.png', image_app_dir_qq + 'qq_yes_contact_100.png',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_100.png', '', '', image_app_dir_line + 'line_yes_contact_100.png'],
            [image_app_dir_wechat + 'wechat_yes_contact_125.png', image_app_dir_qq + 'qq_yes_contact_125.png',
             '', image_app_dir_wechat + 'wechat_yes_contact_125.png', image_app_dir_qq + 'qq_yes_contact_125.png',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_125.png', '', '', image_app_dir_line + 'line_yes_contact_125.png'],
            [image_app_dir_wechat + 'wechat_yes_contact_150.png', image_app_dir_qq + 'qq_yes_contact_150.png',
             '', image_app_dir_wechat + 'wechat_yes_contact_150.png', image_app_dir_qq + 'qq_yes_contact_150.png',
             '', '', '', '', image_app_dir_ding6 + 'ding6_yes_contact_150.png', '', '', image_app_dir_line + 'line_yes_contact_150.png']
        ]
        yes_group_icons = [
            [image_app_dir_wechat + 'wechat_yes_group_100.png', image_app_dir_qq + 'qq_yes_group_100.png',
             '', image_app_dir_wechat + 'wechat_yes_group_100.png', image_app_dir_qq + 'qq_yes_group_100.png'],
            [image_app_dir_wechat + 'wechat_yes_group_125.png', image_app_dir_qq + 'qq_yes_group_125.png',
             '', image_app_dir_wechat + 'wechat_yes_group_125.png', image_app_dir_qq + 'qq_yes_group_125.png'],
            [image_app_dir_wechat + 'wechat_yes_group_150.png', image_app_dir_qq + 'qq_yes_group_150.png',
             '', image_app_dir_wechat + 'wechat_yes_group_150.png', image_app_dir_qq + 'qq_yes_group_150.png']
        ]
        ding6_copy = [image_app_dir_ding6 + 'ding6_copy_100.png', image_app_dir_ding6 + 'ding6_copy_125.png',
                      image_app_dir_ding6 + 'ding6_copy_150.png']

        ding6_contact_prompt = [image_app_dir_ding6 + 'ding_contact_100.png', image_app_dir_ding6 + 'ding_contact_125.png',
                                image_app_dir_ding6 + 'ding_contact_150.png']

        weibo_send_image_button = image_app_dir_weibo + 'weibo_send_image_button.png'
        yes_wechat_public_icon = [
            image_app_dir_wechat + 'wechat_public_account_100.png',
            image_app_dir_wechat + 'wechat_public_account_125.png',
            image_app_dir_wechat + 'wechat_public_account_150.png'
        ]
        wechat_public_btn_image = [
            image_app_dir_wechat + 'wechat_public_btn_100.png',
            image_app_dir_wechat + 'wechat_public_btn_125.png',
            image_app_dir_wechat + 'wechat_public_btn_150.png'
        ]

        add_service_btn_image = [
            image_app_dir + '/qq/add_service_btn_100.png',
        ]

        add_people_btn_image = [
            image_app_dir + '/qq/add_people_btn_100.png',
        ]

        qq_contact_exist = [
            image_app_dir + '/qq/qq_contact_exist_100.png',
        ]

        qq_search_next = [
            image_app_dir + '/qq/qq_search_next_100.png',
        ]

        tiktok_video_search = [
            image_app_dir_tiktok + '/tiktok_video_search_100.png',
        ]

        tiktok_like_image = [
            image_app_dir_tiktok + '/tiktok_like_image_100.png',
        ]

        tiktok_video_tab = [
            image_app_dir_tiktok + '/tiktok_video_tab_100.png',
        ]

        tiktok_reply = [
            image_app_dir_tiktok + '/tiktok_reply_image_100.png',
        ]

        tiktok_follow = [
            image_app_dir_tiktok + '/tiktok_follow_image_100.png',
        ]

        tiktok_unfollow = [
            image_app_dir_tiktok + '/tiktok_unfollow_image_100.png',
        ]

        tiktok_bottom = [
            image_app_dir_tiktok + '/tiktok_bottom_image_100.png',
        ]

        tiktok_at_sign = [
            image_app_dir_tiktok + '/tiktok_at_sign_100.png',
        ]

        kuaishou_video_tab = [
            image_app_dir_kuaishou + '/kuaishou_video_tab_100.png',
        ]

        kuaishou_reply = [
            image_app_dir_kuaishou + '/kuaishou_reply_image_100.png',
        ]

        kuaishou_bottom = [
            image_app_dir_kuaishou + '/kuaishou_bottom_image_100.png',
        ]

        kuaishou_follow = [
            image_app_dir_kuaishou + '/kuaishou_follow_image_100.png',
        ]

        kuaishou_video_like = [
            image_app_dir_kuaishou + '/kuaishou_video_like_image_100.png',
        ]

        kuaishou_wan = [
            image_app_dir_kuaishou + '/kuaishou_wan_100.png'
        ]

        kuaishou_follow_eachother = [
            image_app_dir_kuaishou + '/kuaishou_follow_eachother_100.png',
        ]

        kuaishou_unfollow = [
            image_app_dir_kuaishou + '/kuaishou_unfollow_image_100.png',
        ]

        slide_image_tiktok = image_app_dir_tiktok + 'tiktok_code_slide.png'

    rpa_task_timer = 0
    rpa_task_monitor = 1

    scale_ratio = 1

    app_type_wechat = 0
    app_type_qq = 1
    app_type_ding = 2
    app_type_wechat_gray = 3
    app_type_qq_full = 4
    app_type_ding_gray = 5
    app_type_ding_full = 6
    app_type_weibo = 7
    app_type_momo = 8
    app_type_ding6 = 9
    app_type_51job = 10
    app_type_whatsapp = 11
    app_type_line = 12

    app_type_tiktok = 13
    app_type_kuaishou = 14

    app_total_count = 13

    image_app_dir_dict = {
        app_type_wechat: image_app_dir_wechat,
        app_type_qq: image_app_dir_qq,
        app_type_ding: image_app_dir_ding,
        app_type_wechat_gray: image_app_dir_wechat,
        app_type_qq_full: image_app_dir_qq,
        app_type_ding_gray: image_app_dir_ding,
        app_type_ding_full: image_app_dir_ding,
        app_type_weibo: image_app_dir_weibo,
        app_type_momo: image_app_dir_momo,
        app_type_ding6: image_app_dir_ding6,
        app_type_51job: image_app_dir_51job,
        app_type_whatsapp: image_app_dir_whatsapp,
        app_type_line: image_app_dir_line
    }

    rpa_timer_offset = [()] * app_total_count
    rpa_timer_offset[app_type_wechat] = (110, 35, 90)
    rpa_timer_offset[app_type_qq] = (50, 22, 90)
    rpa_timer_offset[app_type_ding] = (120, 60, 120)
    rpa_timer_offset[app_type_wechat_gray] = (120, 35, 90)
    rpa_timer_offset[app_type_qq_full] = (50, 22, 90)
    rpa_timer_offset[app_type_ding_gray] = (120, 60, 120)
    rpa_timer_offset[app_type_ding_full] = (120, 60, 120)
    rpa_timer_offset[app_type_weibo] = (120, 95, 120)
    rpa_timer_offset[app_type_momo] = (120, 88, 54)
    rpa_timer_offset[app_type_ding6] = (24, 20, 130)
    rpa_timer_offset[app_type_51job] = (219, 100, 90)
    rpa_timer_offset[app_type_whatsapp] = (120, 110, 140)
    rpa_timer_offset[app_type_line] = (167, 77, 95)

    search_point_offset = [[]] * app_total_count
    search_point_offset[app_type_wechat] = [110, 35]
    search_point_offset[app_type_qq] = [50, 12]
    search_point_offset[app_type_ding] = [120, 60]
    search_point_offset[app_type_wechat_gray] = [120, 35]
    search_point_offset[app_type_qq_full] = [50, 22]
    search_point_offset[app_type_ding_gray] = [120, 60]
    search_point_offset[app_type_ding_full] = [120, 60]
    search_point_offset[app_type_weibo] = [120, 95]
    search_point_offset[app_type_momo] = [120, 88]
    search_point_offset[app_type_ding6] = [24, 20]
    search_point_offset[app_type_51job] = [145, 30]
    search_point_offset[app_type_whatsapp] = [146, 52]
    search_point_offset[app_type_line] = [75, 18]

    app_type_dict = [0] * app_total_count
    app_type_dict[app_type_wechat] = 1
    app_type_dict[app_type_qq] = 2
    app_type_dict[app_type_ding] = 3
    app_type_dict[app_type_wechat_gray] = 1
    app_type_dict[app_type_qq_full] = 2
    app_type_dict[app_type_ding_gray] = 3
    app_type_dict[app_type_ding_full] = 3
    app_type_dict[app_type_weibo] = 4
    app_type_dict[app_type_momo] = 5
    app_type_dict[app_type_ding6] = 3
    app_type_dict[app_type_51job] = 7
    app_type_dict[app_type_whatsapp] = 8
    app_type_dict[app_type_line] = 9

    title_offset = [0] * app_total_count
    title_offset[app_type_wechat] = 70
    title_offset[app_type_qq] = 85
    title_offset[app_type_ding] = 100
    title_offset[app_type_wechat_gray] = 70
    title_offset[app_type_qq_full] = 85
    title_offset[app_type_ding_gray] = 100
    title_offset[app_type_ding_full] = 100
    title_offset[app_type_weibo] = 55
    title_offset[app_type_momo] = 0
    title_offset[app_type_ding6] = 90
    title_offset[app_type_51job] = 75
    title_offset[app_type_whatsapp] = 90
    title_offset[app_type_line] = 110

    # 应用最小的长宽，输入框离四个边缘最短距离(上下左右)
    app_min_region = [0] * app_total_count
    app_min_region[app_type_wechat] = ([700, 500], [70, 130, 310, 370])
    app_min_region[app_type_qq] = ([500, 495], [162, 115, 60, 440])
    app_min_region[app_type_ding] = ([798, 602], [300, 105, 276, 475])
    app_min_region[app_type_wechat_gray] = ([700, 500], [70, 130, 310, 370])
    app_min_region[app_type_qq_full] = ([500, 495], [162, 115, 60, 440])
    app_min_region[app_type_ding_gray] = ([798, 602], [300, 105, 276, 475])
    app_min_region[app_type_ding_full] = ([798, 602], [300, 105, 276, 475])
    app_min_region[app_type_weibo] = ([816, 159], [0, 159, 316, 500])
    app_min_region[app_type_momo] = ([816, 159], [0, 159, 316, 500])
    app_min_region[app_type_ding6] = ([798, 602], [300, 105, 276, 475])
    app_min_region[app_type_51job] = ([798, 602], [300, 105, 276, 475])
    app_min_region[app_type_whatsapp] = ([654, 515], [300, 105, 276, 475])
    app_min_region[app_type_line] = ([746, 493], [300, 105, 276, 475])

    wand_threshold = AiConfig.wand_threshold
    for i in range(len(wand_threshold)):
        if i == app_type_momo:
            wand_threshold[i] = (0, 35)
        elif i == app_type_ding6:
            wand_threshold[i] = (0, 0)
        elif i == app_type_51job:
            wand_threshold[i] = (5, 5)

    send_button_offset = [[64, 16]] * app_total_count
    send_button_offset[app_type_wechat] = [64, 16]
    send_button_offset[app_type_qq] = [64, 30]
    send_button_offset[app_type_ding] = [64, 16]
    send_button_offset[app_type_wechat_gray] = [64, 16]
    send_button_offset[app_type_qq_full] = [64, 16]
    send_button_offset[app_type_ding_gray] = [64, 16]
    send_button_offset[app_type_ding_full] = [64, 16]
    send_button_offset[app_type_weibo] = [64, 40]
    send_button_offset[app_type_momo] = [45, 58]
    send_button_offset[app_type_ding6] = [164, 35]
    send_button_offset[app_type_51job] = [100, 25]
    send_button_offset[app_type_whatsapp] = [37, 42]
    send_button_offset[app_type_line] = [37, 32]

    find_logo_random = random.randrange(16, 32, 1)
    weibo_search_height = 32
    ding5_message_button_offset_x = 30
    ding5_message_button_offset_y = 112
    ding6_send_button_offset = 120

    default_msg = "请您访问http://saas.landingbj.com，新建或维护您的渠道、用户信息"
    default_flag = False

    sample_icon_size = 20
    input_icon_offset = [60, 20]
    attach_app_index = 0

    yes_contact_images = []
    yes_group_images = []
    no_contact_images = []
    ding6_prompt_images = []
    yes_contact_bin_images = []
    yes_group_bin_images = []
    yes_wechat_public_bin_images = None
    no_contact_bin_images = []
    ding6_prompt_bin_images = []
    scale_ratio_index = 0

    qq_banner_height = 36
    qq_cross_length = 9

    rpa_robot_flag = 1
    rpa_timer_flag = 1
    rpa_monitor_flag = 1

    topmost_matrix = []

    line_new_dial_offset = 75

    channel_name = 'qa'
    channel_user = 'demo'
    login_status = ''

    robot_frame_height = 125
    qa_frame_height = 160

    selected_app_type = []

    whatsapp_title_height = 30
    input_click_offset = 50
    red_round_size = 15

    def __init__(self):
        self.__dialogue_region = []
        self.__input_region = []
        self.__app_region = []
        self.__contact_region = []
        self.__app_type = []
        self.__period = 0
        self.__channel_name = 'qa'
        self.__channel_user = 'demo'
        self.__search_pos = []
        self.__icon_pos = []
        self.__send_btn_pos = []
        self.__search_sample = []
        self.__icon_sample = []
        self.__send_btn_sample = []
        self.__bin_search_sample = []
        self.__bin_icon_sample = []
        self.__bin_send_btn_sample = []

    @property
    def search_sample(self):
        return self.__search_sample

    @property
    def icon_sample(self):
        return self.__icon_sample

    @property
    def send_btn_sample(self):
        return self.__send_btn_sample

    @property
    def bin_search_sample(self):
        return self.__bin_search_sample

    @property
    def bin_icon_sample(self):
        return self.__bin_icon_sample

    @property
    def bin_send_btn_sample(self):
        return self.__bin_send_btn_sample

    @property
    def search_pos(self):
        return self.__search_pos

    @property
    def icon_pos(self):
        return self.__icon_pos

    @property
    def send_btn_pos(self):
        return self.__send_btn_pos

    @property
    def channel_name(self):
        return self.__channel_name

    @channel_name.setter
    def channel_name(self, name):
        self.__channel_name = name

    @property
    def channel_user(self):
        return self.__channel_user

    @channel_user.setter
    def channel_user(self, user):
        self.__channel_user = user

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, second):
        self.__period = second

    @property
    def dialogue_region(self):
        self.__dialogue_region = []
        for i in range(len(self.app_region)):
            dial_x = self.__input_region[i][0]
            dial_y = self.app_region[i][1] + Config.title_offset[self.app_type[i]]
            dial_w = self.__input_region[i][2]
            dial_h = self.__input_region[i][1] - dial_y
            self.__dialogue_region.append((dial_x, dial_y, dial_w, dial_h))
        return self.__dialogue_region

    @property
    def contact_region(self):
        self.__contact_region = []
        for i in range(len(self.app_region)):
            dial_x = self.__app_region[i][0]
            dial_y = self.__app_region[i][1]
            dial_w = self.__input_region[i][0] - self.__app_region[i][0]
            dial_h = self.__app_region[i][3]
            self.__contact_region.append((dial_x, dial_y, dial_w, dial_h))
        return self.__contact_region

    @property
    def input_region(self):
        return self.__input_region

    @input_region.setter
    def input_region(self, region):
        self.__input_region = region

    @property
    def app_region(self):
        return self.__app_region

    @app_region.setter
    def app_region(self, region):
        self.__app_region = region

    @property
    def app_type(self):
        return self.__app_type

    def __str__(self):
        return str(self.__period) + ", " + self.__channel_name + ", " + self.__channel_user