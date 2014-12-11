# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
from utility import run_shell, cp, fix_rpath, safe_remove
from requirement import RequirementException
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ni_install_dir = os.path.join(robustus.cache, 'OpenNI2')
    if requirement_specifier.version is not None:
        ni_install_dir += requirement_specifier.version

    def in_cache():
        return os.path.isfile(os.path.join(ni_install_dir, 'libOpenNI2.so'))

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
                    raise RequirementException('OpenNI2 clone failed')
            os.chdir(ni_clone_dir)

            # checkout requested version
            branch = requirement_specifier.version if requirement_specifier.version is not None else 'master'
            if requirement_specifier.version is not None:
                retcode = run_shell(['git', 'checkout', branch])
                if retcode != 0:
                    raise RequirementException('OpenNI2 checkout failed')

            logging.info('Building OpenNI')
            if platform.machine().startswith('arm'):
                ver = 'Arm'
                # patch flags for arm
                file_to_patch = os.path.join(ni_clone_dir, 'ThirdParty/PSCommon/BuildSystem/Platform.Arm')
                with open(file_to_patch, "rt") as f:
                    content = f.read()
                with open(file_to_patch, "wt") as f:
                    f.write(content.replace('-mfloat-abi=softfp', ''))
            elif platform.architecture()[0].startswith('64'):
                ver = 'x64'
            else:
                ver = 'x86'
            retcode = run_shell(['make', 'PLATFORM=' + ver], verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('OpenNI2 build failed')

            # copy release dir and usb rules to wheelhouse
            if os.path.isdir(ni_install_dir):
                shutil.rmtree(ni_install_dir)
            release_dir = os.path.join(ni_clone_dir, 'Bin', ver + '-Release')
            shutil.copytree(release_dir, ni_install_dir)
            cp(os.path.join(ni_clone_dir, 'Packaging/Linux/primesense-usb.rules'), ni_install_dir)
        finally:
            os.chdir(cwd)
            safe_remove(ni_clone_dir)

    # copy files to venv
    if in_cache():
        logging.info('Copying OpenNI2 to virtualenv')
        cp(os.path.join(ni_install_dir, '*.so'), os.path.join(robustus.env, 'lib'))
        cp(os.path.join(ni_install_dir, '*.jar'), os.path.join(robustus.env, 'lib'))
        ni_drivers_dir = os.path.join(robustus.env, 'lib/OpenNI2')
        if os.path.isdir(ni_drivers_dir):
            shutil.rmtree(ni_drivers_dir)
        shutil.copytree(os.path.join(ni_install_dir, 'OpenNI2'), ni_drivers_dir)
        # copy demo for testing purposes
        cp(os.path.join(ni_install_dir, 'SimpleRead'), os.path.join(robustus.env, 'bin'))
        fix_rpath(robustus, robustus.env, os.path.join(robustus.env, 'bin/SimpleRead'), os.path.join(robustus.env, 'lib'))  
        # setup usb rules
        logging.info('Configuring udev rules, you may need to reconnect sensor or restart computer')
        retcode = run_shell(['sudo', 'cp', os.path.join(ni_install_dir, 'primesense-usb.rules'), '/etc/udev/rules.d/557-primesense-usb.rules'], verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('Faied to copy udev rules')
        # return nonzero code, but seems to work
        subprocess.call(['sudo', 'udevadm', 'control', '--reload-rules'])
    else:
        raise RequirementException('can\'t find OpenNI2-%s in robustus cache' % requirement_specifier.version)
