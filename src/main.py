#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# main.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#
import logging
import sys
from tkinter import Tk

from landingbj.agent_config import AgentConfig
from landingbj.gui import Main
from landingbj.config import Config
from ai.config import AiConfig
import json
import os

from ai.image import generate_logo

if __name__ == '__main__':
    try:
        import pyi_splash
        pyi_splash.update_text('UI Loaded ...')
        pyi_splash.close()
    except:
        pass

    conf = Config()

    # directory = 'rpa_debug'
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    #
    # logging.basicConfig(handlers=[logging.FileHandler(filename="rpa_debug/rpa_debug.log",
    #                                                   encoding='utf-8', mode='a'),
    #                               logging.StreamHandler()],
    #                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    #
    # logging.getLogger("PIL").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("zeep").setLevel(logging.WARNING)
    # logging.info('Version: 2022.07.20 v1041')

    if os.path.exists('config.json'):
        with open('config.json') as config_file:
            config_dict = json.load(config_file)
            conf.channel_name = config_dict['channel_name']
            conf.channel_user = config_dict['channel_user']
            Config.channel_name = config_dict['channel_name']
            Config.channel_user = config_dict['channel_user']
            Config.rpa_robot_flag = config_dict['rpa_robot_flag']
            Config.rpa_timer_flag = config_dict['rpa_timer_flag']
            Config.rpa_monitor_flag = config_dict['rpa_monitor_flag']
            if 'login_status' in config_dict:
                Config.login_status = config_dict['login_status']
    else:
        Config.channel_name = 'qa'
        Config.channel_user = 'demo'

    generate_logo(AiConfig.cube_logo_size)

    root = Tk()
    if sys.platform == 'win32':
        root.iconbitmap(Config.image_gui_dir + '/icon.ico')
    root.title("聊天助理")

    directory = AgentConfig.guide_url_tmp_dir
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    my_gui = Main(root, conf)
    root.mainloop()
