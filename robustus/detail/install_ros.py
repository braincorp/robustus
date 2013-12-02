# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
import shutil
import subprocess


def install(robustus, requirement_specifier, rob_file, ignore_index):
    rosdep = os.path.join(robustus.env, 'bin/rosdep')
    rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
    wstool = os.path.join(robustus.env, 'bin/wstool')
    if not os.path.isfile(rosinstall_generator)\
       or not os.path.isfile(rosdep)\
       or not os.path.isfile(wstool):
        raise RequirementException('To install ros you need rosinstall_generator, rosdep, etc.\n'
                                   'Here is the full list of dependencies ROS requires:\n'
                                   '    rosinstall==0.6.30\n'
                                   '    rosinstall_generator==0.1.4\n'
                                   '    wstool==0.0.4')

    def in_cache():
        devel_dir = os.path.join(robustus.cache, 'ros-%s' % requirement_specifier.version, 'devel_isolated')
        return os.path.isdir(devel_dir)

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
            # rosdep initialization requires sudo, so should be installed and iniailized separately
            # subprocess.call(rosdep + ' init', shell=True)

            # update ros dependencies
            retcode = subprocess.call(rosdep + ' update', shell=True)
            if retcode != 0:
                raise RequirementException('Failed to update ROS dependencies')

            # install bare bones ROS
            retcode = subprocess.call(rosinstall_generator + ' desktop --rosdistro %s' % v
                                      + ' --deps --wet-only > %s-ros_comm-wet.rosinstall' % v, shell=True)
            if retcode != 0:
                raise RequirementException('Failed to generate rosinstall file')

            retcode = subprocess.call(wstool + ' init -j8 src %s-ros_comm-wet.rosinstall' % v, shell=True)
            if retcode != 0:
                raise RequirementException('Failed to build ROS')

            # resolve dependencies
            retcode = subprocess.call(rosdep + ' install --from-paths src --ignore-src --rosdistro %s -y' % v, shell=True)
            if retcode != 0:
                raise RequirementException('Failed to resolve ROS dependencies')

        # create catkin workspace
        rosdir = os.path.join(robustus.env, 'ros')
        catkin_make_isolated = os.path.join(ros_cache, 'src/catkin/bin/catkin_make_isolated')
        retcode = subprocess.call(catkin_make_isolated + ' --install-space %s --install' % rosdir, shell=True)
        if retcode != 0:
            raise RequirementException('Failed to create catkin workspace for ROS')
        os.chdir(cwd)
    except RequirementException:
        os.chdir(cwd)
        shutil.rmtree(ros_cache)
