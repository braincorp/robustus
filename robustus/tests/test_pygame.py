# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_pygame_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('Pygame==1.9.1', ['pygame'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
