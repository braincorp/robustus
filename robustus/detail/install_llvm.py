# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    cwd = os.getcwd()
    os.chdir(robustus.cache)
    llvm_archive = 'llvm-%s.src.tar.gz' % requirement_specifier.version
    subprocess.call(['wget', '-c', 'http://llvm.org/releases/%s/%s' % (requirement_specifier.version, llvm_archive)])
    llvm_install_dir = os.path.join(robustus.cache, 'llvm-%s' % requirement_specifier.version)
    if not os.path.isdir(llvm_install_dir) and not ignore_index:
        subprocess.call(['tar', 'zxvf', llvm_archive])
        llvm_src_dir = 'llvm-%s.src' % requirement_specifier.version
        os.chdir(llvm_src_dir)
        os.mkdir(llvm_install_dir)
        subprocess.call(['./configure', '--enable-optimized', '--prefix', llvm_install_dir])
        subprocess.call('REQUIRES_RTTI=1 make install', shell=True)
        os.chdir(robustus.cache)
        shutil.rmtree(llvm_src_dir)
    os.environ['LLVM_CONFIG_PATH'] = os.path.join(llvm_install_dir, 'bin/llvm-config')
    os.chdir(cwd)
