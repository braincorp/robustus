# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
from requirement import RequirementException
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
                                   '    rosdep==0.10.23\n'
                                   '    rosinstall_generator==0.1.4\n'
                                   '    wstool==0.0.4')

    # rosdep may also be initialized resulting into failure, that's ok
    subprocess.call(rosdep + ' init', shell=True)

    # update ros dependencies
    retcode = subprocess.call(rosdep + ' update', shell=True)
    if retcode != 0:
        raise RequirementException('Failed to update ROS dependencies')

    # install bare bones ROS
    v = requirement_specifier.version
    retcode = subprocess.call([rosinstall_generator + ' ros_comm --rosdistro %s'
                               ' --deps --wet-only > %s-ros_comm-wet.rosinstall' % (v, v)])
    if retcode != 0:
        raise RequirementException('Failed to generate rosinstall file')
    retcode = subprocess.call([wstool +' init -j8 src %s-ros_comm-wet.rosinstall' % v])
    if retcode != 0:
        raise RequirementException('Failed to generate rosinstall file')
