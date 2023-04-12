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

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(module_list="landingbj/*.py", exclude='landingbj/__init__.py'),
)
