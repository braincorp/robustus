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


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
