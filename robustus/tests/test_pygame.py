# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import glob
import os
import pytest
import robustus
import shutil


def test_bullet_installation():
    cwd = os.getcwd()
    test_env = 'test_env'
    if os.path.isdir(test_env):
        shutil.rmtree(test_env)

    # create env and install bullet into it
    robustus.execute(['env', test_env])
    robustus.execute(['--env', test_env, 'install', 'Pygame==1.9.1'])
    # pygame is not cached for now, just check that it has been installed
    assert os.path.isdir(os.path.join(test_env, 'lib/python2.7/site-packages/pygame'))
    assert os.path.isfile(os.path.join(test_env, 'lib/python2.7/site-packages/pygame/display.so'))

    os.chdir(cwd)
    shutil.rmtree(test_env)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
