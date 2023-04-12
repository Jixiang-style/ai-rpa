# cython: language_level=3
import copy
import logging
import os
import shutil
from pathlib import Path

from PIL import Image
from ai.config import AiConfig
from ai.image_match import icon_match

from landingbj.config import Config
import pyautogui as pg


def detect(pool, screenshot, input_region):
    if Config.scale_ratio == 1.25:
        idx = 1
    elif Config.scale_ratio == 1.5:
        idx = 2
    else:
        idx = 0

    result = detect_by_scale(pool, screenshot, input_region, idx)
    return result


def detect_by_scale(pool, screenshot, input_region, index):
    # 获取一批缩放尺寸的各APP图片
    dial_button_icon = Config.dial_button_icons[index]
    button_height = 50 * Config.scale_ratio + 5
    search_region = (input_region[0], input_region[1] - button_height, input_region[2] // 2, button_height * 2)

    future_list = []
    for i in range(0, len(dial_button_icon)):
        dial_icon = Path(dial_button_icon[i])
        if not dial_icon.is_file():
            continue
        future = submit_task(pool, dial_button_icon[i], screenshot, input_region, search_region, i)
        future_list.append(future)

    for f in future_list:
        if f.result() > -1:
            logging.info('detect_by_scale %s' % f.result())
            return f.result()
    return detect_by_version(pool, screenshot, input_region, index)


def detect_by_version(pool, screenshot, input_region, index):
    button_height = 50 * Config.scale_ratio + 5
    search_region = (input_region[0], input_region[1] - button_height, input_region[2] // 2, button_height * 2)

    dial_button_icon = Config.dial_button_icons[index]
    dial_button_icons = {}

    for i, icon in enumerate(dial_button_icon):
        dial_icon_list = []
        image_name = Path(icon).name
        app_dir = Path(Config.image_app_dir_dict[i]).parent
        sub_app_folders = sorted([f.path for f in os.scandir(app_dir) if f.is_dir() and f.name != 'default'],
                                 reverse=True)
        for folder in sub_app_folders:
            root_dir, version = os.path.split(folder)
            dial_icon = {'root_dir': root_dir, 'version': version, 'image': image_name}
            dial_icon_list.append(dial_icon)
        dial_button_icons[i] = dial_icon_list

    future_list = []
    for i, dial_icon_list in dial_button_icons.items():
        for j in range(0, len(dial_icon_list)):
            root_dir = dial_icon_list[j]['root_dir']
            version = dial_icon_list[j]['version']
            dial_icon = root_dir + '/' + version + '/' + dial_icon_list[j]['image']
            dial_icon_path = Path(dial_icon)
            if not dial_icon_path.is_file():
                continue
            future = submit_task(pool, dial_icon, screenshot, input_region, search_region, i)
            future_list.append([future, root_dir, version])

    for f in future_list:
        if f[0].result() > -1:
            shutil.copytree(f[1] + '/' + f[2], f[1] + '/default', dirs_exist_ok=True)
            logging.info(f[1] + '/' + f[2])
            return f[0].result()
    return -1


def submit_task(pool, dial_icon, screenshot, input_region, search_region, i):
    # 因为所有的预处理都是单独生成额外图像，copy操作似乎没有必要
    # screenshot_temp = copy.deepcopy(screenshot)

    screenshot_temp = screenshot
    if i == Config.app_type_51job:
        future = pool.submit(app_type_detect_51job, dial_icon, screenshot_temp, input_region, i)
    elif i == Config.app_type_weibo:
        future = pool.submit(app_type_detect_weibo, dial_icon, screenshot_temp, input_region, i)
    # elif i == Config.app_type_ding6:
    #     future = pool.submit(app_type_detect_ding6, dial_icon, screenshot_temp, input_region, i)
    elif i == Config.app_type_qq:
        future = pool.submit(app_type_detect_qq, dial_icon, screenshot_temp, input_region, i)
    # elif i == Config.app_type_qq_full:
    #     future = pool.submit(app_type_detect_qq, dial_icon, screenshot_temp, input_region, i)
    # elif i == Config.app_type_whatsapp:
    #     future = pool.submit(app_type_detect_whatsapp, dial_icon, screenshot_temp, input_region, i)
    # elif i == Config.app_type_line:
    #     future = pool.submit(app_type_detect_line, dial_icon, screenshot_temp, input_region, i)
    else:
        future = pool.submit(app_type_detect, dial_icon, screenshot_temp, search_region, i)
    return future


def app_type_detect(dial_icon_path, screenshot, search_region, i):
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    pos_list = list(pg.locateAll(dial_icon_path, screenshot, region=search_region, grayscale=True))
    logging.info('app_type_detect %s, %s' % (i, pos_list))
    if len(pos_list) > 0:
        return i
    dial_icon_path = Config.dial_button_icons[0][i]
    pos_list = list(pg.locateAll(dial_icon_path, screenshot, region=search_region, grayscale=True))
    if len(pos_list) > 0:
        reset_config(i)
        return i
    return -1


def app_type_detect_line(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1] + input_region[3] // 2,
                     input_region[0] + input_region[2] // 2, input_region[1] + input_region[3])
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, icon, search_region, AiConfig.line_binarize_threshold,
                             AiConfig.match_ratio_line)
    if flag:
        if abs(ratio - 1) > 0.2:
            reset_config(i)
        return i
    return -1


def app_type_detect_whatsapp(dial_icon_path, screenshot, input_region, i):
    search_region = (
        input_region[0], input_region[1], input_region[0] + input_region[2] // 2, input_region[1] + input_region[3])
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, icon, search_region, AiConfig.whatsapp_binarize_threshold,
                             AiConfig.match_ratio_whatsapp)
    if flag:
        if abs(ratio - 1) > 0.2:
            reset_config(i)
        return i
    return -1


def app_type_detect_ding6(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1],
                     input_region[0] + input_region[2] // 2, input_region[1] + input_region[3] // 4)
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, icon, search_region, AiConfig.ding6_binarize_threshold,
                             AiConfig.match_ratio_ding6)
    if flag:
        if abs(ratio - 1) > 0.2:
            reset_config(i)
        return i
    return -1


def app_type_detect_qq(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1],
                     input_region[0] + input_region[2] // 2, input_region[1] + input_region[3] // 4)
    icon = Image.open(dial_icon_path).convert('L')
    logging.info('search_region %s, %s' % (str(search_region), dial_icon_path))
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    flag, ratio = icon_match(screenshot, icon, search_region, AiConfig.qq_binarize_threshold, 0.7)
    if flag:
        if abs(ratio - 1) > 0.2:
            reset_config(i)
        return i
    return -1


def app_type_detect_weibo(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1], input_region[0] + input_region[2] / 2,
                     input_region[1] + input_region[3] / 4)
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    weibo_icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, weibo_icon, search_region,
                             AiConfig.weibo_binarize_threshold, 0.85)
    if flag:
        Config.weibo_search_height = Config.weibo_search_height * ratio
        return Config.app_type_weibo
    return -1


def app_type_detect_51job(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1],
                     input_region[0] + input_region[2] / 2, input_region[1] + input_region[3] / 4)
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, icon, search_region, AiConfig.job51_binarize_threshold,
                             0.85)
    if flag:
        return Config.app_type_51job
    return -1


def app_type_detect_momo(dial_icon_path, screenshot, input_region, i):
    search_region = (input_region[0], input_region[1],
                     input_region[0] + input_region[2] / 2, input_region[1] + input_region[3] / 4)
    if search_region[0] == search_region[2] or search_region[1] == search_region[3]:
        return -1
    momo_icon = Image.open(dial_icon_path).convert('L')
    flag, ratio = icon_match(screenshot, momo_icon, search_region, AiConfig.momo_binarize_threshold,
                             AiConfig.momo_match_ratio)
    if flag:
        return Config.app_type_momo
    return -1


def reset_config(i):
    a = Config.rpa_timer_offset[i][0] / Config.scale_ratio
    b = Config.rpa_timer_offset[i][1] / Config.scale_ratio
    c = Config.rpa_timer_offset[i][2] / Config.scale_ratio
    Config.rpa_timer_offset[i] = (a, b, c)
    for j in range(len(Config.search_point_offset[i])):
        Config.search_point_offset[i][j] = Config.search_point_offset[i][j] / Config.scale_ratio
    Config.title_offset[i] = Config.title_offset[i] / Config.scale_ratio
    for j in range(len(Config.app_min_region[i])):
        for k in range(len(Config.app_min_region[i][j])):
            Config.app_min_region[i][j][k] = Config.app_min_region[i][j][k] / Config.scale_ratio
    if i not in (Config.app_type_wechat, Config.app_type_wechat_gray):
        for j in range(len(Config.send_button_offset[i])):
            Config.send_button_offset[i][j] = Config.send_button_offset[i][j] / Config.scale_ratio
    if Config.scale_ratio == 1.25:
        Config.dial_button_icons[1][i] = Config.dial_button_icons[0][i]
        if i < len(Config.no_contact_icons[1]):
            Config.no_contact_icons[1][i] = Config.no_contact_icons[0][i]
        if i < len(Config.yes_contact_icons[1]):
            Config.yes_contact_icons[1][i] = Config.yes_contact_icons[0][i]
        if i < len(Config.yes_group_icons[1]):
            Config.yes_group_icons[1][i] = Config.yes_group_icons[0][i]
        if i == Config.app_type_ding6:
            Config.ding6_copy[1] = Config.ding6_copy[0]
            Config.ding6_contact_prompt[1] = Config.ding6_contact_prompt[0]
    elif Config.scale_ratio == 1.5:
        Config.dial_button_icons[2][i] = Config.dial_button_icons[0][i]
        if i < len(Config.no_contact_icons[1]):
            Config.no_contact_icons[2][i] = Config.no_contact_icons[0][i]
        if i < len(Config.yes_contact_icons[1]):
            Config.yes_contact_icons[2][i] = Config.yes_contact_icons[0][i]
        if i < len(Config.yes_group_icons[1]):
            Config.yes_group_icons[2][i] = Config.yes_group_icons[0][i]
        if i == Config.app_type_ding6:
            Config.ding6_copy[2] = Config.ding6_copy[0]
            Config.ding6_contact_prompt[2] = Config.ding6_contact_prompt[0]
