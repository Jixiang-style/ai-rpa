# cython: language_level=3
import configparser

from landingbj.config import Config, resource_path


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config


def get_int_tuple(s):
    return tuple(map(int, s.split(',')))


def get_app_drag_data(app_region, initial_left_up_pos, relative_drag_pos):
    app_drag_data = {}
    for key in initial_left_up_pos:
        left_up_pos_x, left_up_pos_y = initial_left_up_pos[key]
        relative_drag_pos_x, relative_drag_pos_y = relative_drag_pos[key]
        app_region_x, app_region_y = app_region[key][0], app_region[key][1]
        drag_pos_x, drag_pos_y = left_up_pos_x + relative_drag_pos_x, left_up_pos_y + relative_drag_pos_y
        drag_data = (drag_pos_x, drag_pos_y, app_region_x - left_up_pos_x, app_region_y - left_up_pos_y)
        app_drag_data[key] = drag_data
    return app_drag_data


def get_initial_app_region(app_region, initial_left_up_pos):
    initial_app_region = {}
    for key in initial_left_up_pos:
        left_up_pos_x, left_up_pos_y = initial_left_up_pos[key]
        width, height = app_region[key][2], app_region[key][3]
        drag_data = (left_up_pos_x, left_up_pos_y, left_up_pos_x + width, left_up_pos_y + height)
        initial_app_region[key] = drag_data
    return initial_app_region


def rel_to_abs_pos(base_pos, rel_pos):
    result = list(rel_pos)
    result[0] = result[0] + base_pos[0]
    result[1] = result[1] + base_pos[1]
    return tuple(result)


def add_browser_tab(app_id, tab_id, override=False):
    browser_tab = AgentConfig.browser_tab
    if app_id in browser_tab and tab_id in browser_tab[app_id] and not override:
        return

    for app in browser_tab:
        for i in range(len(browser_tab[app])):
            if browser_tab[app][i] >= tab_id:
                browser_tab[app][i] = browser_tab[app][i] + 1

    if app_id not in browser_tab:
        browser_tab[app_id] = [tab_id]
    else:
        browser_tab[app_id].append(tab_id)
    browser_tab[app_id].sort()


def remove_browser_tab(app_id, tab_id):
    browser_tab = AgentConfig.browser_tab
    if app_id not in browser_tab:
        return
    for app in browser_tab:
        for tab in browser_tab[app]:
            if tab == tab_id:
                browser_tab[app].remove(tab_id)
    for app in browser_tab:
        for i in range(len(browser_tab[app])):
            if browser_tab[app][i] >= tab_id:
                browser_tab[app][i] = browser_tab[app][i] - 1


class AgentConfig:
    INIT_STATE = 0
    GET_QR_CODE_SUCCESS = 10
    NUMBER_CODE_MOBILE = 20
    NUMBER_CODE_APP = 21
    NUMBER_CODE_MOBILE_AUTO = 22
    LOGIN_SUCCESS = 100
    SUCCESS = 1
    FAILED = 0

    APP_NAME = {
        Config.app_type_wechat: 'WeChat.exe',
        Config.app_type_qq: 'QQ.exe',
        Config.app_type_ding6: 'Dingtalk.exe',
        Config.app_type_weibo: '',
        Config.app_type_51job: '',
        Config.app_type_whatsapp: 'WhatsApp.exe',
        Config.app_type_line: 'LINE.exe',
    }

    config = load_config(resource_path() + 'rpa_agent.ini')

    chrome_path = config['CHROME']['chrome_path']
    chrome_tmp_dir = config['CHROME']['chrome_tmp_dir']
    chrome_window_size = config['CHROME']['chrome_window_size']
    chrome_window_position = config['CHROME']['chrome_window_position']
    chrome_window_xy = get_int_tuple(chrome_window_position) + get_int_tuple(chrome_window_size)
    chrome_title_bar_xy = chrome_window_xy[0] + 800, chrome_window_xy[1] + 60

    initial_left_up_pos = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_initial_left_up_pos']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_initial_left_up_pos']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_initial_left_up_pos']),
        Config.app_type_whatsapp: get_int_tuple(config['POSITION']['whatsapp_initial_left_up_pos']),
        Config.app_type_line: get_int_tuple(config['POSITION']['line_initial_left_up_pos'])
    }

    start_frame_left_up = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_start_frame_left_up']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_start_frame_left_up']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_start_frame_left_up']),
        Config.app_type_weibo: get_int_tuple(config['CHROME']['chrome_window_position']),
        Config.app_type_51job: get_int_tuple(config['CHROME']['chrome_window_position']),
        Config.app_type_whatsapp: get_int_tuple(config['POSITION']['whatsapp_start_frame_left_up']),
        Config.app_type_line: get_int_tuple(config['POSITION']['line_start_frame_left_up']),
        Config.app_type_tiktok: get_int_tuple(config['CHROME']['chrome_window_position']),
        Config.app_type_kuaishou: get_int_tuple(config['CHROME']['chrome_window_position']),
    }

    qr_code_region = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_qr_code_region']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_qr_code_region']),
        Config.app_type_weibo: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                              get_int_tuple(config['POSITION']['weibo_qrcode_rel_pos'])),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_qr_code_region']),
        Config.app_type_51job: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                              get_int_tuple(config['POSITION']['51job_qrcode_rel_pos'])),
        Config.app_type_whatsapp: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                                 get_int_tuple(config['POSITION']['whatsapp_qrcode_rel_pos'])),
        Config.app_type_line: rel_to_abs_pos(start_frame_left_up[Config.app_type_line],
                                             get_int_tuple(config['POSITION']['line_qrcode_rel_pos'])),
        Config.app_type_tiktok: rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                             get_int_tuple(config['TIKTOK']['tiktok_qrcode_rel_pos'])),
        Config.app_type_kuaishou: rel_to_abs_pos(start_frame_left_up[Config.app_type_kuaishou],
                                             get_int_tuple(config['KUAISHOU']['kuaishou_qrcode_rel_pos'])),
    }

    qrcode_btn_pos = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_qrcode_btn_pos']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_qr_code_btn_pos']),
        Config.app_type_weibo: get_int_tuple(config['POSITION']['weibo_qr_code_btn_pos']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_qr_code_btn_pos']),
        Config.app_type_51job: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                              get_int_tuple(config['POSITION']['51job_qrcode_rel_btn_pos'])),
        Config.app_type_kuaishou: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                                 get_int_tuple(config['KUAISHOU']['kuaishou_qrcode_rel_btn_pos'])),
    }

    verification_code_region = {
        Config.app_type_line: get_int_tuple(config['POSITION']['line_vcode_rel_pos'])
    }

    username_pos = {
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_username_pos']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_username_pos']),
        Config.app_type_weibo: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                              get_int_tuple(config['POSITION']['weibo_rel_username_pos'])),
        Config.app_type_51job: get_int_tuple(config['POSITION']['51job_username_pos']),
        Config.app_type_line: rel_to_abs_pos(start_frame_left_up[Config.app_type_line],
                                             get_int_tuple(config['POSITION']['line_username_rel_pos'])),
        Config.app_type_tiktok: rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                             get_int_tuple(config['TIKTOK']['tiktok_username_rel_pos'])),
        Config.app_type_kuaishou: rel_to_abs_pos(start_frame_left_up[Config.app_type_kuaishou],
                                             get_int_tuple(config['KUAISHOU']['kuaishou_username_rel_pos'])),
    }

    valid_code_btn_region = {
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_valid_code_btn_region']),
        Config.app_type_weibo: rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                              get_int_tuple(config['POSITION']['weibo_rel_valid_code_btn_region'])),
        Config.app_type_51job: get_int_tuple(config['POSITION']['51job_valid_code_btn_region'])
    }

    login_logo_region = {
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_login_logo_region']),
        Config.app_type_qq: rel_to_abs_pos(get_int_tuple(config['POSITION']['qq_main_panel_pos']),
                                              get_int_tuple(config['POSITION']['qq_login_logo_rel_region']))
    }

    app_default_username = {
        Config.app_type_wechat: '文件传输助手', Config.app_type_ding6: '我'
    }

    app_path = {
        Config.app_type_wechat: config['APP_PATH']['wechat_path'],
        Config.app_type_qq: config['APP_PATH']['qq_path'],
        Config.app_type_ding6: config['APP_PATH']['ding_path'],
        Config.app_type_whatsapp: config['APP_PATH']['whatsapp_path'],
        Config.app_type_line: config['APP_PATH']['line_path']
    }

    app_region = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_app_region']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_app_region']),
        Config.app_type_weibo: get_int_tuple(config['POSITION']['weibo_app_region']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_app_region']),
        Config.app_type_51job: get_int_tuple(config['POSITION']['51job_app_region']),
        Config.app_type_whatsapp: get_int_tuple(config['POSITION']['whatsapp_app_region']),
        Config.app_type_line: get_int_tuple(config['POSITION']['line_app_region']),
        Config.app_type_tiktok: chrome_window_xy,
        Config.app_type_kuaishou: chrome_window_xy,
    }

    input_region = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_input_region']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_input_region']),
        Config.app_type_weibo: get_int_tuple(config['POSITION']['weibo_input_region']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_input_region']),
        Config.app_type_51job: get_int_tuple(config['POSITION']['51job_input_region']),
        Config.app_type_whatsapp: get_int_tuple(config['POSITION']['whatsapp_input_region']),
        Config.app_type_line: get_int_tuple(config['POSITION']['line_input_region']),
        Config.app_type_tiktok: (0, 0, 0, 0),
        Config.app_type_kuaishou: (0, 0, 0, 0)
    }

    qq_main_panel_x, qq_main_panel_y = get_int_tuple(config['POSITION']['qq_main_panel_pos'])
    weibo_account_btn_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                           get_int_tuple(config['POSITION']['weibo_rel_account_btn_pos']))
    account_btn_pos_51job = get_int_tuple(config['POSITION']['51job_account_btn_pos'])
    slide_search_region_51job = get_int_tuple(config['POSITION']['51job_slide_search_region'])
    slide_search_region_qq = rel_to_abs_pos(start_frame_left_up[Config.app_type_qq],
                                get_int_tuple(config['POSITION']['slide_search_rel_region_qq']))

    meituan_account_btn_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                             get_int_tuple(config['MEITUAN']['meituan_rel_account_btn_pos']))
    meituan_policy_btn_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['MEITUAN']['meituan_rel_policy_btn_pos']))
    gadugadu_rel_policy_btn_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['GADUGADU']['gadugadu_rel_policy_btn_region']))
    gadugadu_rel_show_login_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['GADUGADU']['gadugadu_rel_show_login_pos']))

    relative_drag_pos = {
        Config.app_type_wechat: get_int_tuple(config['POSITION']['wechat_relative_drag_pos']),
        Config.app_type_qq: get_int_tuple(config['POSITION']['qq_relative_drag_pos']),
        Config.app_type_ding6: get_int_tuple(config['POSITION']['ding_relative_drag_pos']),
        Config.app_type_whatsapp: get_int_tuple(config['POSITION']['whatsapp_relative_drag_pos']),
        Config.app_type_line: get_int_tuple(config['POSITION']['line_relative_drag_pos'])
    }

    app_drag_data = get_app_drag_data(app_region, initial_left_up_pos, relative_drag_pos)
    initial_app_region = get_initial_app_region(app_region, initial_left_up_pos)

    minimize_app = eval(config['DEFAULT']['minimize_app'])
    minimize_app_wait_time = int(config['TIME']['minimize_app_wait_time'])
    debug = eval(config['DEFAULT']['debug'])

    app_index_dict = {
        1: Config.app_type_wechat,
        2: Config.app_type_qq,
        3: Config.app_type_ding6,
        4: Config.app_type_weibo,
        5: Config.app_type_wechat,
        7: Config.app_type_51job,
        8: Config.app_type_whatsapp,
        9: Config.app_type_line,
        10: Config.app_type_tiktok,
        11: Config.app_type_kuaishou,
    }

    slide_region_qq = rel_to_abs_pos(start_frame_left_up[Config.app_type_qq],
                                    get_int_tuple(config['POSITION']['slide_rel_region_qq']))
    slide_btn_x_qq, slide_btn_y_qq = rel_to_abs_pos(start_frame_left_up[Config.app_type_qq],
                                    get_int_tuple(config['POSITION']['slide_btn_rel_pos_qq']))
    slide_refresh_x_qq, slide_refresh_y_qq = rel_to_abs_pos(start_frame_left_up[Config.app_type_qq],
                                    get_int_tuple(config['POSITION']['slide_refresh_rel_pos_qq']))

    slide_search_region_tiktok = rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                                get_int_tuple(config['TIKTOK']['tiktok_slide_search_rel_region']))
    slide_region_tiktok = rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                         get_int_tuple(config['TIKTOK']['tiktok_slide_rel_region']))
    slide_btn_x_tiktok, slide_btn_y_tiktok = rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                    get_int_tuple(config['TIKTOK']['tiktok_slide_btn_rel_pos']))
    slide_refresh_x_tiktok, slide_refresh_y_tiktok = rel_to_abs_pos(start_frame_left_up[Config.app_type_tiktok],
                                    get_int_tuple(config['TIKTOK']['tiktok_slide_refresh_rel_pos']))
    tiktok_slide_theme_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_slide_theme_region']))
    tiktok_slide_drag_offset = int(config['TIKTOK']['tiktok_slide_drag_offset'])
    tiktok_author_fan_max = int(config['TIKTOK']['tiktok_author_fan_max'])
    tiktok_video_like_max = int(config['TIKTOK']['tiktok_video_like_max'])
    tiktok_search_filter_sort_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_search_filter_sort_pos']))
    tiktok_search_filter_time_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_search_filter_time_pos']))
    tiktok_search_filter_btn_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_search_filter_btn_pos']))
    tiktok_author_fan_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_author_fan_pos']))
    tiktok_video_like_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_video_like_pos']))
    tiktok_author_follow_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_author_follow_region']))
    tiktok_avatar_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_avatar_pos']))
    tiktok_id_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_id_pos']))
    tiktok_search_follow_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['TIKTOK']['tiktok_search_follow_region']))
    tiktok_video_tab_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']), (363, 178))

    kuaishou_author_follow_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['KUAISHOU']['kuaishou_author_follow_region']))
    kuaishou_video_like_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['KUAISHOU']['kuaishou_video_like_region']))
    kuaishou_user_icon = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']), (1514, 128))
    kuaishou_author_fan_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']), (243, 452))
    kuaishou_author_fan_max = int(config['TIKTOK']['tiktok_author_fan_max'])
    kuaishou_avatar_pos = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']), (1834, 107))
    kuaishou_search_follow_region = rel_to_abs_pos(get_int_tuple(config['CHROME']['chrome_window_position']),
                                            get_int_tuple(config['KUAISHOU']['kuaishou_search_follow_region']))

    slide_region_51job = (2769, 1216, 3030 - 2769, 1378 - 1216)
    slide_btn_x_51job, slide_btn_y_51job = 2797, 1412
    slide_refresh_x_51job, slide_refresh_y_51job = 2816, 1469
    slide_offset_51job = 4
    slide_duration_51job = 1

    browser_tab = {Config.app_type_tiktok: [1], Config.app_type_kuaishou: [1]}

    qq_panel_drag_offset = get_int_tuple(config['POSITION']['qq_panel_drag_offset'])

    qq_show_close_x, qq_show_close_y = rel_to_abs_pos(initial_left_up_pos[Config.app_type_qq],
                                                      get_int_tuple(config['POSITION']['qq_show_close_rel_pos']))

    qq_roaming_close_x, qq_roaming_close_y = rel_to_abs_pos(initial_left_up_pos[Config.app_type_qq],
                                                      get_int_tuple(config['POSITION']['qq_roaming_close_rel_pos']))

    qq_panel_close_x, qq_panel_close_y = rel_to_abs_pos(get_int_tuple(config['POSITION']['qq_main_panel_pos']),
                                                    get_int_tuple(config['POSITION']['qq_panel_minimize_rel_pos']))

    agent_port_file = eval(config['DEFAULT']['agent_port_file'])
    default_agent_port = eval(config['DEFAULT']['default_agent_port'])

    browser_app = (
        Config.app_type_weibo,
        Config.app_type_51job,
        Config.app_type_whatsapp,
        Config.app_type_tiktok,
        Config.app_type_kuaishou,
    )

    qr_code_default_show = {
        Config.app_type_wechat: 0,
        Config.app_type_ding6: 0,
        Config.app_type_qq: 0,
        Config.app_type_weibo: 1,
        Config.app_type_51job: 0,
        Config.app_type_whatsapp: 1,
        Config.app_type_line: 1,
        Config.app_type_tiktok: 1,
        Config.app_type_kuaishou: 0,
    }

    qq_contact_region = get_int_tuple(config['QQ']['qq_contact_region'])
    guide_wait_min_time = int(config['DEFAULT']['guide_wait_min_time'])
    guide_wait_max_time = int(config['DEFAULT']['guide_wait_max_time'])
    guide_wait_max_count = int(config['DEFAULT']['guide_wait_max_count'])
    log_level = int(config['DEFAULT']['log_level'])
    guide_tmp_dir = eval(config['DEFAULT']['guide_tmp_dir'])
    guide_url_tmp_dir = guide_tmp_dir + '/url'
    guide_tmp_file_dict = {}

    tiktok_max_reply = 50
    kuaishou_max_reply = 50
    tiktok_current_reply = 0
    kuaishou_current_reply = 0
    tiktok_current_count = 0
