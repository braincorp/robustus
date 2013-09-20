# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
import robustus
import shutil


def test_panda_installation(tmpdir):
    tmpdir.chdir()
    test_env = 'test_env'

    # create env and install bullet into it
    robustus.execute(['env', test_env])
    robustus.execute(['--env', test_env, 'install', 'panda3d==1.8.1'])
    # check for panda3d cache
    assert os.path.isdir(os.path.join(test_env, 'wheelhouse/panda3d-1.8.1'))
    assert os.path.isdir(os.path.join(test_env, 'wheelhouse/panda3d-1.8.1/lib'))
    # check that panda3d is installed into env
    assert os.path.isdir(os.path.join(test_env, 'lib/panda3d'))
    assert os.path.isfile(os.path.join(test_env, 'lib/panda3d/panda3d.py'))

    shutil.rmtree(test_env)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
