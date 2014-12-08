# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
from utility import run_shell
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ni_install_dir = os.path.join(robustus.cache, 'OpenNI-%s' % requirement_specifier.version)
    ni2so = os.path.join(ni_install_dir, 'lib/python2.7/site-packages/cv2.so')
    def in_cache():
        return os.path.isfile(ni2so)

    if not in_cache() and not ignore_index:
        try:
            logging.info('Cloning OpenNI')
            retcode = run_shell(['git', 'clone', 'https://github.com/OpenNI/OpenNI2.git'])
            if retcode != 0:
                raise RequirementException('OpenNI clone failed')
            ni_clone_dir = 'OpenNI2'
            os.chdir(ni_clone_dir)

            # checkout requested version
            retcode = run_shell(['git', 'checkout', 'tags/' + requirement_specifier.version])
            if retcode != 0:
                raise RequirementException('OpenNI checkout failed')

            logging.info('Building OpenNI')
            if platform.machine().startswitch('arm'):
                retcode = run_shell(['PLATFORM=Arm make'], verbose=robustus.settings['verbosity'] >= 1)
            else:
                retcode = run_shell(['make', '-j4'], verbose=robustus.settings['verbosity'] >= 1)

            if retcode != 0:
                raise RequirementException('OpenNI build failed')

                logging.info('Building OpenNI')
                cv_build_dir = os.path.join(opencv_archive_name, 'build')
                if not os.path.isdir(cv_build_dir):
                    os.mkdir(cv_build_dir)
                os.chdir(cv_build_dir)
        finally:
            #safe_remove(ni_clone_dir)
            os.chdir(cwd)

