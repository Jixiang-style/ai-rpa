# cython: language_level=3
import time
from sys import platform
from typing import Tuple

import mss
import numpy as np
import pyautogui
import pyscreeze
from PIL import Image, ImageFilter
from ai.image import image_binarize
from pyscreeze import Point

from landingbj.config import Config

current_monitor = 0
monitor_region = {}

with mss.mss() as sct:
    for i in range(1, len(sct.monitors)):
        mon = sct.monitors[i]
        monitor_region[i] = (mon['left'], mon['top'], mon['left'] + mon['width'], mon['top'] + mon['height'])


def get_monitor_index(x: int, y: int) -> i:
    for key, value in monitor_region.items():
        if value[0] < x < value[2] and value[1] < y < value[3]:
            return key
    return -1


def get_monitor_region(monitor: int = None) -> Tuple[int, int, int, int]:
    if monitor is None:
        monitor = current_monitor
    return monitor_region[monitor]


def get_abs_region(region: Tuple[int, ...]) -> Tuple[int, ...]:
    current_monitor_region = get_monitor_region()
    if len(region) == 4:
        result = current_monitor_region[0] + region[0], current_monitor_region[1] + region[1], region[2], region[3]
    else:
        result = current_monitor_region[0] + region[0], current_monitor_region[1] + region[1]
    return result


def screenshot():
    monitor = mss.mss().monitors[current_monitor]
    monitor = {
        "top": monitor["top"],
        "left": monitor["left"],
        "width": monitor["width"],
        "height": monitor["height"],
        "mon": current_monitor,
    }
    sct_img = mss.mss().grab(monitor)
    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return img


def locateAllOnScreen(needle_image, region=None):
    result = list(pyautogui.locateAllOnScreen(needle_image, region=region))
    if len(result) > 0:
        return result
    return locateAll(needle_image, pyscreeze.screenshot(), region)


def locateOnScreen(needle_image, region=None, binarize_threshold=230, threshold=0.8):
    pos = pyautogui.locateOnScreen(needle_image, region=region)
    if pos is not None:
        return pos
    return locate(needle_image, pyscreeze.screenshot(), region,
                  binarize_threshold=binarize_threshold, threshold=threshold)


def locateCenterOnScreen(needle_image, region=None, binarize_threshold=230, threshold=0.8):
    return center(locateOnScreen(needle_image, region, binarize_threshold, threshold))


def center(pos):
    if pos is None:
        return None
    return Point(pos[0] + pos[2] // 2, pos[1] + pos[3] // 2)


def locateAll(needle_image, haystack_image, region=None):
    return locate(needle_image, haystack_image, region, all_flag=True)


def locate(needle_image, haystack_image, region=None, all_flag=False, binarize_threshold=230, threshold=0.8, file_replace=True):
    replace_image = None
    if isinstance(needle_image, str):
        replace_image = needle_image
        needle_image = Image.open(needle_image).convert('L')
    if region is not None:
        haystack_image = haystack_image.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
    else:
        region = (0, 0)
    # needle_array = np.asarray(image_binarize(needle_image, 210))
    # haystack_array = np.asarray(image_binarize(haystack_image, 210))
    # remove_bg(needle_image).show()
    # haystack_image.show()
    # image_binarize(needle_image, binarize_threshold).show()
    # image_binarize(haystack_image, binarize_threshold).show()
    needle_array = np.asarray(image_binarize(needle_image, binarize_threshold))
    haystack_array = np.asarray(image_binarize(haystack_image, binarize_threshold))
    needle_height, needle_width = needle_array.shape
    haystack_height, haystack_width = haystack_array.shape
    count, total_count = 0, needle_height * needle_width * threshold
    result = []
    for k in range(haystack_height - needle_height + 1):
        for j in range(haystack_width - needle_width + 1):
            b = haystack_array[k:k + needle_height, j: j + needle_width]
            tmp_count = np.sum(needle_array == b)
            if tmp_count > total_count:
                pos = [j + region[0], k + region[1], needle_width, needle_height]
                if not all_flag:
                    if file_replace:
                        haystack_image.crop((j, k, j + needle_width, k + needle_height)).save(replace_image)
                    return pos
                result.append(pos)
    if not all_flag:
        return None
    return result


def remove_bg(image, low=50, high=150):
    edge = image.filter(ImageFilter.FIND_EDGES)
    edge.save('edge.png')
    base_array = np.array(image, dtype=int)
    gray_array = np.array(image, dtype=int)
    edge_array = np.asarray(edge, dtype=int)
    conditions = [gray_array < low, gray_array > high]
    choices = [0, 255]
    gray_array = np.select(conditions, choices, gray_array)
    conditions = [edge_array < low, edge_array > high]
    choices = [0, 255]
    edge_array = np.select(conditions, choices, edge_array)
    conditions = [gray_array != edge_array]
    choices = [128]
    data = np.select(conditions, choices, base_array)
    data[:1] = 128
    data[data.shape[0] - 1:data.shape[0]] = 128
    data[:, :1] = 128
    data[:, data.shape[1] - 1:data.shape[1]] = 128
    result = Image.fromarray(data, mode='I').convert('L')
    return result


def click_if_not_link(x, y, clicks=1):
    pyautogui.moveTo(x, y)
    time.sleep(1)
    if platform == "win32":
        import win32gui
        cursor_type = win32gui.GetCursorInfo()[1]
        if cursor_type == Config.windows_cursor_text or cursor_type == Config.windows_cursor_normal:
            pyautogui.click(x, y, clicks=clicks)
            return True
    return False
