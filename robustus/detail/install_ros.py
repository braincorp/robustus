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


def install(robustus, requirement_specifier, rob_file, ignore_index):
    # check distro
    if requirement_specifier.version != 'hydro':
        logging.warn('Robustus is only tested to install ROS hydro.\n'
                     'Still, it will try to install required distribution "%s"' % requirement_specifier.version)

    # install dependencies
    retcode = robustus.execute('install rosinstall==0.6.30 rosinstall_generator==0.1.4 wstool==0.0.4 catkin_pkg')
    if retcode != 0:
        raise RequirementException('Failed to install ROS dependencies')

    def in_cache():
        devel_dir = os.path.join(robustus.cache, 'ros-%s' % requirement_specifier.version, 'devel_isolated')
        return os.path.isdir(devel_dir)

    # ROS installation bloats command log and TRAVIS terminates build
    # FIXME: regular execution for now, change stdout to open('/dev/null') to get rid of log
    def exec_silent(cmd):
        logging.info('executing: ' + cmd)
        return subprocess.call(cmd, shell=True, stdout=sys.stdout, stderr=sys.stdout)

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
            # add ros sources to packages list
            if 'packages.ros.org' not in open('/etc/apt/sources.list.d/ros-latest.list'):
                exec_silent('sudo sh -c echo "deb http://packages.ros.org/ros/ubuntu precise main" > ' \
                            '/etc/apt/sources.list.d/ros-latest.list')
                exec_silent('wget http://packages.ros.org/ros.key -O - | sudo apt-key add -')

            # install rosdep
            rosdep = shutil.which('rosdep')
            if rosdep is None:
                exec_silent('sudo apt-get install python-rosdep')
                retcode = exec_silent('sudo rosdep init')
                if retcode != 0:
                    raise RequirementException('Failed to install rosdep')
                rosdep = shutil.which('rosdep')
            rosdep = 'sudo ' + rosdep

            # update ros dependencies
            retcode = exec_silent(rosdep + ' update')
            if retcode != 0:
                raise RequirementException('Failed to update ROS dependencies')

            # install bare bones ROS
            # FIXME: desktop version takes too long to build on TRAVIS
            # 'ros_comm' if 'TRAVIS' in os.environ else 'desktop'
            rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
            dist = 'desktop'
            retcode = exec_silent(rosinstall_generator + ' %s --rosdistro %s' % (dist, v)
                                  + ' --deps --wet-only > %s-ros_comm-wet.rosinstall' % v)
            if retcode != 0:
                raise RequirementException('Failed to generate rosinstall file')

            wstool = os.path.join(robustus.env, 'bin/wstool')
            retcode = exec_silent(wstool + ' init -j8 src %s-ros_comm-wet.rosinstall' % v)
            if retcode != 0:
                raise RequirementException('Failed to build ROS')

            # resolve dependencies
            retcode = exec_silent(rosdep + ' install --from-paths src --ignore-src --rosdistro %s -y' % v)
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
