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
from robustus.detail.utility import safe_move


def install(robustus, requirement_specifier, rob_file, ignore_index):
    cwd = os.getcwd()
    os.chdir(robustus.cache)

    install_dir = os.path.join(robustus.cache, 'protobuf-%s' % requirement_specifier.version)

    # try to download precompiled protobuf from the remote cache first
    if not os.path.isdir(install_dir) and not ignore_index:
        protobuf_archive = robustus.download_compiled_archive('protobuf', requirement_specifier.version)
        if protobuf_archive is not None:
            unpack(protobuf_archive)
            logging.info('Initializing compiled protobuf')
            # install into wheelhouse
            if not os.path.exists(install_dir):
                raise RequirementException("Failed to unpack precompiled protobuf archive")

    if not os.path.isdir(install_dir) and not ignore_index:
        archive_name = 'protobuf-%s.tar.gz' % requirement_specifier.version
        if os.path.exists(archive_name):
            safe_remove(archive_name)
        # move sources to a folder in order to use a clean name for installation
        src_dir = 'protobuf-%s' % requirement_specifier.version
        if os.path.exists(src_dir):
            safe_remove(src_dir)
        run_shell(['wget', 'https://protobuf.googlecode.com/svn/rc/%s' % (archive_name,)],
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

        retcode = run_shell(['./configure', '--disable-shared',
                             'CFLAGS=-fPIC',
                             'CXXFLAGS=-fPIC',
                             '--prefix', install_dir],
                            verbose=robustus.settings['verbosity'] >= 1)

        if retcode:
            raise RequirementException('Failed to configure protobuf compilation')
        retcode = run_shell('make', shell=True,
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode:
            raise RequirementException('Failed compile protobuf')

        retcode = run_shell('make install', shell=True)
        if retcode:
            raise RequirementException('Failed install protobuf')

        os.chdir(robustus.cache)
        shutil.rmtree(src_dir)

    venv_install_folder = os.path.join(robustus.env, 'protobuf')
    if os.path.exists(venv_install_folder):
        safe_remove(venv_install_folder) 
    shutil.copytree(install_dir, venv_install_folder)
    executable_path = os.path.join(install_dir, 'bin', 'protoc')
    ln(executable_path, os.path.join(robustus.env, 'bin', 'protoc'), force=True)
    os.chdir(cwd)

    # now install python part
    robustus.install_through_wheeling(requirement_specifier, rob_file, ignore_index)
