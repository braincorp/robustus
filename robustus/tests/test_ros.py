# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


@pytest.mark.skipif("'TRAVIS' in os.environ")
def test_ros_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import rospy',
               'import boto']
    dependencies = ['boto==2.19.0']  # boto is just to ensure that non-ROS requirements are also in venv
    
    perform_standard_test('ros==hydro.ros_comm',
                          imports,
                          [],
                          dependencies,
                          postinstall_script='. test_env/bin/activate && . test_env/ros/setup.sh')


@pytest.mark.skipif("'TRAVIS' in os.environ")
def test_gscam_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import rospy',
               'import boto']
    dependencies = ['boto==2.19.0', 'ros==hydro.ros_comm',
                    'opencv==2.4.4', 'numpy==1.7.1', 'sip']
    
    perform_standard_test(['ros_overlay=https://github.com/ros-drivers/gscam.git#3d976c80324f5723cd7a23c18d452c4231044cc0,https://github.com/ros/nodelet_core.git#71a90d671e49f6e4b8b73d4e856f6335e9511dba'],
                          imports,
                          [],
                          dependencies,
                          postinstall_script='. test_env/bin/activate && . test_env/ros/setup.sh')


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
