# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import shutil
import subprocess


def install(robustus, version, rob_file):
    cwd = os.getcwd()
    os.chdir(robustus.cache)
    llvm_archive = 'llvm-%s.src.tar.gz' % version
    subprocess.call(['wget', '-c', 'http://llvm.org/releases/%s/%s' % (version, llvm_archive)])
    llvm_install_dir = os.path.join(robustus.cache, 'llvm-%s' % version)
    if not os.path.isdir(llvm_install_dir):
        subprocess.call(['tar', 'zxvf', llvm_archive])
        llvm_src_dir = 'llvm-%s.src' % version
        os.chdir(llvm_src_dir)
        os.mkdir(llvm_install_dir)
        subprocess.call(['./configure', '--enable-optimized', '--prefix', llvm_install_dir])
        subprocess.call('REQUIRES_RTTI=1 make install', shell=True)
        shutil.rmtree(llvm_src_dir)
    os.environ['LLVM_CONFIG_PATH'] = os.path.join(llvm_install_dir, 'bin/llvm-config')
    os.chdir(cwd)