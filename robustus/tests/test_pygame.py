# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
import robustus
from robustus.detail import check_module_available
import shutil


def test_pygame_installation(tmpdir):
    tmpdir.chdir()
    test_env = 'test_env'

    # create env and install bullet into it
    robustus.execute(['env', test_env])
    robustus.execute(['--env', test_env, 'install', 'Pygame==1.9.1'])
    # pygame is not cached for now, just check that it has been installed
    assert os.path.isdir(os.path.join(test_env, 'lib/python2.7/site-packages/pygame'))
    assert os.path.isfile(os.path.join(test_env, 'lib/python2.7/site-packages/pygame/display.so'))
    assert check_module_available(test_env, 'pygame')

    shutil.rmtree(test_env)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
