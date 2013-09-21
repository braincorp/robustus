# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_bullet_installation(tmpdir):
    tmpdir.chdir()
    bullet_files = ['lib/bullet-2.81/lib/libBulletCollision.a',
                    'lib/bullet-2.81/lib/libBulletDynamics.a',
                    'lib/bullet-2.81/lib/libLinearMath.a']
    perform_standard_test('bullet==2.81', [], bullet_files)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
