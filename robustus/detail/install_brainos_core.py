# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================
import sys
import os
from robustus.detail import run_shell, RequirementException, fix_rpath


def install(robustus, requirement_specifier, rob_file, ignore_index):
    cmake_options = []
    if sys.platform.startswith('linux'):
        cmake_options = ['-DCMAKE_C_COMPILER=/usr/bin/gcc-4.9',
                         '-DCMAKE_CXX_COMPILER=/usr/bin/g++-4.9',
                         '-DBRAINOS_BUILD_NODES=OFF']

    robustus.install_cmake_package(requirement_specifier,
                                   cmake_options,
                                   ignore_index,
                                   clone_url='git@github.com:braincorp/brainos_core.git')

    # patch rpaths
    fix_rpath(robustus, robustus.env, os.path.join(robustus.env, 'bin/brainosd'), os.path.join(robustus.env, 'lib'))

    # install python part of brainos_core
    url = 'git+ssh://git@github.com/braincorp/brainos_core.git'
    if requirement_specifier.version is not None:
        url += '@' + requirement_specifier.version
    retcode = run_shell([robustus.pip_executable, 'install', url])
    if retcode != 0:
        raise RequirementException('Failed to install python part of brainos2_core')
