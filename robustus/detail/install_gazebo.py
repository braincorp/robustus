# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
from utility import fix_rpath, ln


def install(robustus, requirement_specifier, rob_file, ignore_index):
    install_dir = robustus.install_cmake_package(requirement_specifier,
                                                 ['-DENABLE_TESTS_COMPILATION:BOOL=False'],
                                                 ignore_index)

    # required gazebo executables
    executables = ['gazebo', 'gzserver', 'gzclient', 'gzfactory', 'gzlog', 'gzsdf', 'gzstats', 'gztopic']

    # fix rpaths for binaries
    lib_dir = os.path.join(install_dir, 'lib')
    binaries = glob.glob(os.path.join(install_dir, 'lib/*.so*'))
    for executable in executables:
        binaries += glob.glob(os.path.join(install_dir, 'bin/' + executable + '*'))
    for binary in binaries:
        if os.path.isfile(binary) and not os.path.islink(binary):
            fix_rpath(robustus.env, binary, lib_dir)

    # make symlinks
    for executable in executables:
        executable_path = os.path.join(install_dir, 'bin', executable)
        ln(executable_path, os.path.join(robustus.env, 'bin', executable))
