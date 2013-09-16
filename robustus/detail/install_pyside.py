# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import subprocess
import sys


def install(robustus, requirement_specifier, rob_file):
    robustus.install_through_wheeling(requirement_specifier, rob_file)

    # need links to shared libraries
    cwd = os.getcwd()
    pyside_setup_dir = os.path.join(robustus.cache, 'pyside-setup-master')
    if not os.path.isdir(pyside_setup_dir):
        os.chdir(robustus.cache)
        subprocess.call(['wget',
                         '-c',
                         'https://github.com/PySide/pyside-setup/archive/master.zip',
                         '-O', 'pyside-setup-master.zip'])
        subprocess.call(['unzip', 'pyside-setup-master.zip'])
        os.chdir(pyside_setup_dir)
        subprocess.call([sys.executable, 'pyside_postinstall.py', '-install'])
        os.chdir(cwd)