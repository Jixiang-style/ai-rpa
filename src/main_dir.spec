# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\Workspaces\\Landingbj\\ai_rpa\\src'],
             binaries=[],
             datas=[('resource', '.')],
             hiddenimports=['landingbj.screen_util', 'landingbj.message_box', 'landingbj.gui_module','landingbj.repeater_frame','landingbj.robot_frame',
                            'landingbj.setting_frame','landingbj.timer_frame','landingbj.app_detect', 'landingbj.autogui',
                            'landingbj.resource_sync', 'ai.image_match', 'ai.kmeans', 'ai.new_message', 'landingbj.qa', 'landingbj.rpa',
                            'tkinter.messagebox', 'tkinter.filedialog','tkinter.font', 'tkinter.ttk', 'numpy', 'PIL.Image','ttkthemes',
                            'pyautogui', 'zeep', 'win32gui', 'win32con', 'landingbj.util', 'win32clipboard', 'mss',
                            'landingbj.contact_frame', 'landingbj.social_rpa', 'landingbj.agent_browser', 'landingbj.agent_config'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['lib2to3', 'sqlite3', 'win32ui', 'win32wnet',
                     'win32evtlog', 'win32pdh', 'win32trace'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

excluded_binaries = ['ucrtbase.dll', 'mfc140u.dll', 'lxml.sax', 'lxml.objectify']
a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='banban.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          icon='resource/gui/icon.ico',
          version='my_file_version_info.txt',
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=["vcruntime140.dll"],
               name='banban')