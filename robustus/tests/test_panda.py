# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_panda_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('panda3d==1.8.1', ['panda3d'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
