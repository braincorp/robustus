# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
from utility import unpack, safe_remove, run_shell, ln 
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    cwd = os.getcwd()
    os.chdir(robustus.cache)

    install_dir = os.path.join(robustus.cache, 'vowpal_wabbit-%s' % requirement_specifier.version)

    # try to download precompiled Vowpal Wabbit from the remote cache first
    if not os.path.isdir(install_dir) and not ignore_index:
        wabbit_archive = robustus.download_compiled_archive('vowpal_wabbit', requirement_specifier.version)
        if wabbit_archive is not None:
            unpack(wabbit_archive)
            logging.info('Initializing compiled vowpal_wabbit')
            # install into wheelhouse
            if not os.path.exists(install_dir):
                raise RequirementException("Failed to unpack precompiled vowpal_wabbit archive")

    if not os.path.isdir(install_dir) and not ignore_index:
        archive_name = '%s.tar.gz' % requirement_specifier.version  # e.g. "7.7.tar.gz"
        if os.path.exists(archive_name):
            safe_remove(archive_name)
        # move sources to a folder in order to use a clean name for installation
        src_dir = 'vowpal_wabbit-%s' % requirement_specifier.version
        if os.path.exists(src_dir):
            safe_remove(src_dir)
        run_shell(['wget', 'https://github.com/JohnLangford/vowpal_wabbit/archive/%s' % (archive_name,)],
                  verbose=robustus.settings['verbosity'] >= 1)
        run_shell(['tar', 'zxvf', archive_name],
                  verbose=robustus.settings['verbosity'] >= 1)

        if os.path.exists(src_dir+'_src'):
            safe_remove(src_dir+'_src')

        shutil.move(src_dir, src_dir+'_src')
        src_dir += '_src'

        os.chdir(src_dir)
        if os.path.exists(install_dir):
            safe_remove(install_dir)
        os.mkdir(install_dir)

        retcode = run_shell(['make'], verbose=robustus.settings['verbosity'] >= 1)

        if retcode:
            raise RequirementException('Failed to compile Vowpal Wabbit')
            
        retcode = run_shell('make install', shell=True)
        if retcode:
            raise RequirementException('Failed install Vowpal Wabbit')

        os.chdir(robustus.cache)
        shutil.rmtree(src_dir)

    venv_install_folder = os.path.join(robustus.env, 'vowpal_wabbit')
    if os.path.exists(venv_install_folder):
        safe_remove(venv_install_folder) 
    shutil.copytree(install_dir, venv_install_folder)
    executable_path = os.path.join(install_dir, 'bin', 'vw')
    ln(executable_path, os.path.join(robustus.env, 'bin', 'vw'), force=True)
    os.chdir(cwd)

    # now install python part
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
