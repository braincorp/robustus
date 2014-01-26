
# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import sys
import platform
from utility import run_shell, add_source_ref


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ver, dist = requirement_specifier.version.split('.')

    # check distro
    if ver != 'hydro':
        logging.warn('Robustus is only tested to install ROS hydro.\n'
                     'Still, it will try to install required distribution "%s"' % requirement_specifier.version)

    # install dependencies, may throw
    robustus.execute(['install',
                      'catkin_pkg==0.1.24',
                      'rosinstall==0.6.30',
                      'rosinstall_generator==0.1.4',
                      'wstool==0.0.4',
                      'empy==3.3.2',
                      'rosdep==0.10.24'])

    def in_cache():
        devel_dir = os.path.join(robustus.cache, 'ros-%s' % requirement_specifier.version, 'devel_isolated')
        return os.path.isdir(devel_dir)

    try:
        cwd = os.getcwd()

        # create ros cache
        ros_cache = os.path.join(robustus.cache, 'ros-%s' % requirement_specifier.version)
        if not os.path.isdir(ros_cache):
            os.mkdir(ros_cache)
        os.chdir(ros_cache)

        # build ros if necessary
        if not in_cache() and not ignore_index:
            rosdep = os.path.join(robustus.env, 'bin/rosdep')
            if rosdep is None:
                raise RequirementException('Failed to find rosdep')

            # add ros package sources
            if sys.platform.startswith('linux') and not os.path.isfile('/etc/apt/sources.list.d/ros-latest.list'):
                ubuntu_distr = platform.linux_distribution()[2]
                os.system('sudo sh -c \'echo "deb http://packages.ros.org/ros/ubuntu %s main"'
                          ' > /etc/apt/sources.list.d/ros-latest.list\'' % ubuntu_distr)
                os.system('wget http://packages.ros.org/ros.key -O - | sudo apt-key add -')
                os.system('sudo apt-get update')

            # init rosdep, rosdep can already be initialized resulting in error, that's ok
            os.system('sudo ' + rosdep + ' init')

            # update ros dependencies
            retcode = run_shell(rosdep + ' update',
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to update ROS dependencies')

            # install desktop version of ROS
            rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
            retcode = run_shell(rosinstall_generator + ' %s --rosdistro %s' % (dist, ver)
                                + ' --deps --wet-only > %s-%s-wet.rosinstall' % (dist, ver),
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to generate rosinstall file')

            wstool = os.path.join(robustus.env, 'bin/wstool')
            retcode = run_shell(wstool + ' init -j8 src %s-%s-wet.rosinstall' % (dist, ver),
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to build ROS')

            # resolve dependencies
            retcode = run_shell(rosdep + ' install -r --from-paths src --ignore-src --rosdistro %s -y' % ver,
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                if platform.machine() == 'armv7l':
                    # Due to the lack of LISP machine for ARM we expect some failures
                    logging.info("No LISP on ARM. Expected not all dependencies to be installed.")
                else:
                    raise RequirementException('Failed to resolve ROS dependencies')

        # create catkin workspace
        rosdir = os.path.join(robustus.env, 'ros')
        py_activate_file = os.path.join(robustus.env, 'bin', 'activate')
        catkin_make_isolated = os.path.join(ros_cache, 'src/catkin/bin/catkin_make_isolated')
        retcode = run_shell('. ' + py_activate_file + ' && ' +
                            catkin_make_isolated + ' --install-space %s --install' % rosdir,
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('Failed to create catkin workspace for ROS')
        os.chdir(cwd)

        # Add ROS settings to activate file
        add_source_ref(robustus, os.path.join(robustus.env, 'ros', 'setup.sh'))
    except RequirementException:
        os.chdir(cwd)
        if robustus.settings['debug']:
            logging.info('Not removing folder %s due to debug flag.' % ros_cache)
        else:
            shutil.rmtree(ros_cache)
        raise
