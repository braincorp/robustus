# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import subprocess
from utility import unpack


def install(robustus, requirement_specifier, rob_file, ignore_index):
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)

    # need links to shared libraries
    pyside_setup_dir = os.path.join(robustus.cache, 'pyside-setup-master')
    if not os.path.isdir(pyside_setup_dir) and not ignore_index:
        os.chdir(robustus.cache)
        pyside_setup_archive = robustus.download('pyside-setup', 'master')
        unpack(pyside_setup_archive)

    cwd = os.getcwd()
    try:
        # run postinstall
        if not os.path.isdir(pyside_setup_dir):
            raise RequirementException('can\'t find pyside-%s in robustus cache' % requirement_specifier.version)
        os.chdir(pyside_setup_dir)
        retcode = subprocess.call([robustus.python_executable, 'pyside_postinstall.py', '-install'])
        if retcode != 0:
            raise RequirementException('failed to execute pyside postinstall script')
    finally:
        os.chdir(cwd)
