# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_panda_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    imports = ['import rospy',
               'from geometry_msgs.msg import Twist']
    dependencies = ['rosinstall==0.6.30',
                    'rosdep==0.10.23',
                    'rosinstall_generator==0.1.4',
                    'wstool==0.0.4']
    
    perform_standard_test('ros==hydro', imports, [], dependencies)


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
