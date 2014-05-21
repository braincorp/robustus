# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


# Simplest test to check basic functionality
def test_pep8_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('pep8', ['import pep8'], [], [])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
