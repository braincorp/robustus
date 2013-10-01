# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_bullet_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    bullet_versions = ['bc2', '2.81']
    for ver in bullet_versions:
        bullet_files = ['lib/bullet-%s/lib/libBulletCollision.a' % ver,
                        'lib/bullet-%s/lib/libBulletDynamics.a' % ver,
                        'lib/bullet-%s/lib/libLinearMath.a' % ver]
        perform_standard_test('bullet==%s' % ver, [], bullet_files)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
