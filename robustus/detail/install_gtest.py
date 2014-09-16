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

    install_dir = os.path.join(robustus.cache, 'gtest-%s' % requirement_specifier.version)
    if not os.path.isdir(install_dir) and not ignore_index:
        archive_name = 'gtest-%s.zip' % requirement_specifier.version
        subprocess.call(['wget', '-c', 'https://googletest.googlecode.com/files/%s' % (archive_name,)])
        
        subprocess.call(['unzip', archive_name])
        
        # move sources to a folder in order to use a clean name for installation
        src_dir = 'gtest-%s' % requirement_specifier.version

        shutil.move(src_dir, src_dir + '_src')
        src_dir += '_src'

        src_dir = os.path.abspath(src_dir)
        os.mkdir(install_dir)
        os.chdir(src_dir)          
        subprocess.call('cmake .', shell=True)
        subprocess.call('make', shell=True)
        
        shutil.copy(os.path.join(src_dir, "src/gtest_main.cc"), os.path.join(install_dir, "gtest_main.cc"))
        shutil.copytree(os.path.join(src_dir, "include"), os.path.join(install_dir, "include"))
        shutil.copy(os.path.join(src_dir, "libgtest.a"), os.path.join(install_dir, "libgtest.a"))
        shutil.copy(os.path.join(src_dir, "libgtest_main.a"), os.path.join(install_dir, "libgtest_main.a"))
        
        os.chdir(robustus.cache)
        shutil.rmtree(src_dir)

    venv_install_folder = os.path.join(robustus.env, 'gtest')
    if os.path.exists(venv_install_folder):
        shutil.rmtree(venv_install_folder) 
    shutil.copytree(install_dir, venv_install_folder)

    os.chdir(cwd)
