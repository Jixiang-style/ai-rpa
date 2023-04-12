#
# This program is commercial software; you can only redistribute it and/or modify
# it under the WARRANTY of Beijing Landing Technologies Co. Ltd.

# You should have received a copy license along with this program;
# If not, write to Beijing Landing Technologies, service@landingbj.com.
#

#
# setup.py

# Copyright (C) 2020 Beijing Landing Technologies, China
#

from setuptools import setup

setup(
    name="ai_rpa",
    install_requires=[
        "pyautogui==0.9.50",
        "zeep==3.4.0",
        "Pillow==7.2.0",
        "numpy==1.19.1",
        "pywin32==228",
        "ttkthemes==3.2.2"
    ],
)
