# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================
import sys
from robustus.detail import run_shell, RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # setup platform specific stuff
    if sys.platform.startswith('darwin'):
        retcode = run_shell(['brew', 'install', 'cmake', 'sqlite3', 'boost', 'python', 'boost-python'],
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('Failed to install dependencies for brainos_core')
    elif sys.platform.startswith('linux'):
        cmd = 'sudo apt-get -y install cmake sqlite3 libsqlite3-dev libopencv-dev\n'\
            'sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test\n'\
            'sudo add-apt-repository ppa:boost-latest/ppa\n'\
            'sudo apt-get update\n'\
            'sudo apt-get install gcc-4.9 g++-4.9 boost1.55\n'\
            'sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.9 20\n'\
            'sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 20\n'
        retcode = run_shell(cmd, verbose=robustus.settings['verbosity'] >= 1, shell=True)
        if retcode != 0:
            raise RequirementException('Failed to install dependencies for brainos_core')

    robustus.install_cmake_package(requirement_specifier,
                                   [],
                                   ignore_index,
                                   clone_url='https://github.com/braincorp/brainos_core.git')
