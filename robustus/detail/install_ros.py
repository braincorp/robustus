# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import sys
from utility import run_shell, which


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ver, dist = requirement_specifier.version.split('.')

    # check distro
    if ver != 'hydro':
        logging.warn('Robustus is only tested to install ROS hydro.\n'
                     'Still, it will try to install required distribution "%s"' % requirement_specifier.version)

    # install dependencies, may throw
    robustus.execute(['install',
                      'rosinstall==0.6.30',
                      'rosinstall_generator==0.1.4',
                      'wstool==0.0.4',
                      'catkin_pkg'])

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
            # install rosdep
            rosdep = which('rosdep')
            if rosdep is None:
                if sys.platform.startswith('linux'):
                    # use system package manager
                    if not os.path.isfile('/etc/apt/sources.list.d/ros-latest.list'):
                        os.system('sudo sh -c \'echo "deb http://packages.ros.org/ros/ubuntu precise main"'
                                  ' > /etc/apt/sources.list.d/ros-latest.list\'')
                        os.system('wget http://packages.ros.org/ros.key -O - | sudo apt-key add -')
                        os.system('sudo apt-get update')

                    rosdep = which('rosdep')
                    if rosdep is None:
                        os.system('sudo apt-get install python-rosdep -y')
                else:
                    # on mac use pip
                    os.system('sudo pip install python-rosdep')
            rosdep = which('rosdep')
            if rosdep is None:
                raise RequirementException('Failed to install/find rosdep')

            # init rosdep, rosdep can already be initialized resulting in error, that's ok
            run_shell('sudo ' + rosdep + ' init',
                      verbose=robustus.settings['verbosity'] >= 1)

            # update ros dependencies
            retcode = run_shell(rosdep + ' update',
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to update ROS dependencies')

            # install desktop version of ROS
            rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
            dist = 'desktop'
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
            retcode = run_shell(rosdep + ' install --from-paths src --ignore-src --rosdistro %s -y' % ver,
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to resolve ROS dependencies')

        # create catkin workspace
        rosdir = os.path.join(robustus.env, 'ros')
        catkin_make_isolated = os.path.join(ros_cache, 'src/catkin/bin/catkin_make_isolated')
        retcode = run_shell(catkin_make_isolated + ' --install-space %s --install' % rosdir,
                            verbose=robustus.settings['verbosity'] >= 1)
        if retcode != 0:
            raise RequirementException('Failed to create catkin workspace for ROS')
        os.chdir(cwd)
    except RequirementException:
        os.chdir(cwd)
        shutil.rmtree(ros_cache)
        raise
