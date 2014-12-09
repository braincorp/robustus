# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
from utility import run_shell, cp
from requirement import RequirementException
import sys


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ni_install_dir = os.path.join(robustus.cache, 'OpenNI-%s' % requirement_specifier.version)

    def in_cache():
        return os.path.isfile(os.path.join(ni_install_dir, 'README'))

    if not in_cache() and not ignore_index:
        cwd = os.getcwd()
        ni_clone_dir = os.path.join(cwd, 'OpenNI2')

        try:
            if os.path.isdir(ni_clone_dir):
                logging.warn('Directory for cloning OpenNI found, cloning skipped')
            else:
                logging.info('Cloning OpenNI')
                retcode = run_shell(['git', 'clone', 'https://github.com/occipital/OpenNI2.git'])
                if retcode != 0:
                    raise RequirementException('OpenNI clone failed')
            os.chdir(ni_clone_dir)

            # checkout requested version
            branch = requirement_specifier.version if requirement_specifier.version is not None else 'master'
            if requirement_specifier.version is not None:
                retcode = run_shell(['git', 'checkout', branch])
                if retcode != 0:
                    raise RequirementException('OpenNI checkout failed')

            logging.info('Building OpenNI')
            if platform.machine().startswith('arm'):
                ver = 'arm'
            elif platform.architecture()[0].startswith('64'):
                ver = 'x64'
            else:
                ver = 'x86'
            os.chdir('Packaging')
            retcode = run_shell([sys.executable, 'ReleaseVersion.py', ver], verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('OpenNI build failed')

            # copy the whole dir to wheelhouse
            if not os.path.isdir(ni_install_dir):
                os.mkdir(ni_install_dir)
            cp(ni_clone_dir + '/*', ni_install_dir)
        finally:
            #safe_remove(ni_clone_dir)
            os.chdir(cwd)

    # run setup script from wheelhouse to env

