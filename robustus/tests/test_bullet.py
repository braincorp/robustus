# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

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
    robustus.execute(['--env', test_env, 'install', 'bullet==2.81'])
    # check for bullet cache
    assert os.path.isdir(os.path.join(test_env, 'wheelhouse/bullet-2.81'))
    assert os.path.isfile(os.path.join(test_env, 'wheelhouse/bullet-2.81/lib/libBulletCollision.a'))
    # check that bullet is installed into env
    assert os.path.isdir(os.path.join(test_env, 'lib/bullet-2.81'))
    assert os.path.isfile(os.path.join(test_env, 'lib/bullet-2.81/lib/libBulletCollision.a'))

    os.chdir(cwd)
    shutil.rmtree(test_env)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
