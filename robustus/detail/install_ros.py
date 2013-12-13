# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
from requirement import RequirementException
import shutil
import subprocess
import sys
from utility import which


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # check distro
    if requirement_specifier.version != 'hydro':
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

    # ROS installation bloats command log and TRAVIS terminates build
    # FIXME: regular execution for now, change to avoid log bloating
    def exec_silent(cmd):
        # logging.info('executing: ' + cmd)
        return subprocess.call(cmd, shell=True)

    try:
        cwd = os.getcwd()

        # create ros cache
        v = requirement_specifier.version
        ros_cache = os.path.join(robustus.cache, 'ros-%s' % v)
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
            retcode = os.system('sudo ' + rosdep + ' init')

            # update ros dependencies
            retcode = os.system(rosdep + ' update')
            if retcode != 0:
                raise RequirementException('Failed to update ROS dependencies')

            # install desktop version of ROS
            rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
            dist = 'desktop'
            retcode = exec_silent(rosinstall_generator + ' %s --rosdistro %s' % (dist, v)
                                  + ' --deps --wet-only > %s-%s-wet.rosinstall' % (dist, v))
            if retcode != 0:
                raise RequirementException('Failed to generate rosinstall file')

            wstool = os.path.join(robustus.env, 'bin/wstool')
            retcode = exec_silent(wstool + ' init -j8 src %s-%s-wet.rosinstall' % (dist, v))
            if retcode != 0:
                raise RequirementException('Failed to build ROS')

            # resolve dependencies
            retcode = os.system(rosdep + ' install --from-paths src --ignore-src --rosdistro %s -y' % v)
            if retcode != 0:
                raise RequirementException('Failed to resolve ROS dependencies')

        # create catkin workspace
        rosdir = os.path.join(robustus.env, 'ros')
        catkin_make_isolated = os.path.join(ros_cache, 'src/catkin/bin/catkin_make_isolated')
        retcode = exec_silent(catkin_make_isolated + ' --install-space %s --install' % rosdir)
        if retcode != 0:
            raise RequirementException('Failed to create catkin workspace for ROS')
        os.chdir(cwd)
    except RequirementException:
        os.chdir(cwd)
        shutil.rmtree(ros_cache)
        raise
