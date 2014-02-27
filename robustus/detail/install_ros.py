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
import ros_utils


def _install_ros_deps(robustus):
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

    return rosdep


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
                      'rosdep==0.10.24',
                      'sip'])

    ros_src_dir = os.path.join(robustus.env, 'ros-src-%s' % requirement_specifier.version)
    ros_install_dir = os.path.join(robustus.cache, 'ros-install-%s-%s' % (requirement_specifier.version, ros_utils.hash_path(robustus.env)))

    def in_cache():
        return os.path.isdir(ros_install_dir)

    rosdep = _install_ros_deps(robustus)

    try:
        cwd = os.getcwd()

        logging.info('ROS install dir %s' % ros_install_dir)

        # build ros if necessary
        if not in_cache() and not ignore_index:
            if not os.path.isdir(ros_src_dir):
                os.makedirs(ros_src_dir)
                os.chdir(ros_src_dir)

            rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
            retcode = run_shell(rosinstall_generator + ' %s --rosdistro %s' % (dist, ver)
                                + ' --deps --wet-only > %s-%s-wet.rosinstall' % (dist, ver),
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to generate rosinstall file')

            wstool = os.path.join(robustus.env, 'bin/wstool')
            retcode = run_shell(wstool + ' init -j2 src %s-%s-wet.rosinstall' % (dist, ver),
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
            py_activate_file = os.path.join(robustus.env, 'bin', 'activate')
            catkin_make_isolated = os.path.join(ros_src_dir, 'src/catkin/bin/catkin_make_isolated')
            retcode = run_shell('. ' + py_activate_file + ' && ' +
                                catkin_make_isolated +
                                ' --install-space %s --install' % ros_install_dir,
                                verbose=robustus.settings['verbosity'] >= 1)
            if retcode != 0:
                raise RequirementException('Failed to create catkin workspace for ROS')
        else:
            logging.info('Using ROS from cache %s' % ros_src_dir)

        os.chdir(cwd)

        # Add ROS settings to activate file
        add_source_ref(robustus, os.path.join(ros_install_dir, 'setup.sh'))

    except RequirementException:
        os.chdir(cwd)
        if robustus.settings['debug']:
            logging.info('Not removing folder %s due to debug flag.' % ros_src_dir)
            logging.info('Not removing folder %s due to debug flag.' % ros_install_dir)
        else:
            shutil.rmtree(ros_src_dir, ignore_errors=True)
            shutil.rmtree(ros_install_dir, ignore_errors=True)
        raise
