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
from utility import unpack, safe_remove, safe_move, run_shell, add_source_ref
import ros_utils


def _get_distribution():
    '''
    Because of the bug in travis, platform.linux_distribution() doesn't really work
    '''
    if 'TRAVIS' in os.environ:
        return 'precise'
    else:
        return platform.linux_distribution()[2]


def _install_ros_deps(robustus):
    rosdep = os.path.join(robustus.env, 'bin/rosdep')
    if rosdep is None:
        raise RequirementException('Failed to find rosdep')

    # add ros package sources
    if sys.platform.startswith('linux') and not os.path.isfile('/etc/apt/sources.list.d/ros-latest.list'):
        os.system('sudo sh -c \'echo "deb http://packages.ros.org/ros/ubuntu %s main"'
                  ' > /etc/apt/sources.list.d/ros-latest.list\'' % _get_distribution())
        os.system('wget http://packages.ros.org/ros.key -O - | sudo apt-key add -')
        os.system('sudo apt-get update')

    # init rosdep, rosdep can already be initialized resulting in error, that's ok
    logging.info('BEGIN: Ignore \"ERROR: default sources list file already exists\"...\n')
    os.system('sudo ' + rosdep + ' init')
    logging.info('END: Ignore \"ERROR: default sources list file already exists\".\n')

    # update ros dependencies
    retcode = run_shell(rosdep + ' update',
                        shell=True,
                        verbose=robustus.settings['verbosity'] >= 1)
    if retcode != 0:
        raise RequirementException('Failed to update ROS dependencies')

    return rosdep


def install(robustus, requirement_specifier, rob_file, ignore_index):
    ver, dist = requirement_specifier.version.split('.')

    if platform.machine() == 'armv7l':
    
        # specific code to link ros on bstem
        ros_install_dir = os.path.join('/opt/bstem/bstem.ros', 'ros-install-%s' % requirement_specifier.version)
        if os.path.isdir(ros_install_dir):
            # check distro
            if (ver == 'hydro' and dist == 'ros_comm'):
                # Add ROS settings to activate file
                logging.info('Using ROS system install %s' % ros_install_dir)
                add_source_ref(robustus, os.path.join(ros_install_dir, 'setup.sh'))
                return
            else: 
                logging.warn('armv7l only uses hydro.ros_comm as a ROS system install.\n')
        else: 
            logging.warn('No suitable ROS system install found.\n')
    
    # check distro
    if ver != 'hydro':
        logging.warn('Robustus is only tested to install ROS hydro.\n'
                     'Still, it will try to install required distribution "%s"' % requirement_specifier.version)

    # install dependencies, may throw
    robustus.execute(['install',
                      'catkin_pkg==0.2.2',
                      'rosinstall==0.6.30',
                      'rosinstall_generator==0.1.4',
                      'wstool==0.0.4',
                      'empy==3.3.2',
                      'rosdep==0.10.27',
                      'sip'])

    ros_src_dir = os.path.join(robustus.env, 'ros-src-%s' % requirement_specifier.version)
    req_name = 'ros-install-%s' % requirement_specifier.version
    req_hash = ros_utils.hash_path(robustus.env)
    ros_install_dir = os.path.join(robustus.cache, '%s-%s' % (req_name, req_hash))

    def in_cache():
        return os.path.isdir(ros_install_dir)

    rosdep = _install_ros_deps(robustus)

    try:
        cwd = os.getcwd()

        logging.info('ROS install dir %s' % ros_install_dir)

        # download and install compiled non-system ROS or, if necessary, build ROS
        if not in_cache() and not ignore_index:
            ros_archive = robustus.download_compiled_archive(req_name, req_hash)
            if ros_archive:
                ros_archive_name = unpack(ros_archive)

                logging.info('Initializing compiled ROS in Robustus wheelhouse')
                # install into wheelhouse
                safe_move(ros_archive_name, ros_install_dir)
                safe_remove(ros_archive)
            else:
                logging.info('Building ROS in Robustus wheelhouse')

                if not os.path.isdir(ros_src_dir):
                    os.makedirs(ros_src_dir)
                os.chdir(ros_src_dir)
    
                rosinstall_generator = os.path.join(robustus.env, 'bin/rosinstall_generator')
                retcode = run_shell(rosinstall_generator + ' %s --rosdistro %s' % (dist, ver)
                                    + ' --deps --wet-only > %s-%s-wet.rosinstall' % (dist, ver),
                                    shell=True,
                                    verbose=robustus.settings['verbosity'] >= 1)
                if retcode != 0:
                    raise RequirementException('Failed to generate rosinstall file')
    
                wstool = os.path.join(robustus.env, 'bin/wstool')
                retcode = run_shell(wstool + ' init -j2 src %s-%s-wet.rosinstall' % (dist, ver),
                                    shell=True,
                                    verbose=robustus.settings['verbosity'] >= 1)
                if retcode != 0:
                    raise RequirementException('Failed to build ROS')
    
                # resolve dependencies
                retcode = run_shell(rosdep + ' install -r --from-paths src --ignore-src --rosdistro %s -y --os=ubuntu:%s' %
                                    (ver, _get_distribution()),
                                    shell=True,
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
                                    shell=True,
                                    verbose=robustus.settings['verbosity'] >= 1)

                if retcode != 0:
                    raise RequirementException('Failed to create catkin workspace for ROS')
    
                logging.info('Removing ROS source/build directory %s' % ros_src_dir)
                os.chdir(ros_install_dir)  # NOTE: If this directory is not accessible, something is wrong.
                shutil.rmtree(ros_src_dir, ignore_errors=False)
        else:
            logging.info('Using ROS from cache %s' % ros_install_dir)

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
