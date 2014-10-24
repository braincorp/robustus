# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_vowpal_wabbit_installation(tmpdir):
    tmpdir.chdir()

    wabbit_imports = ['import wabbit_wappa']

    perform_standard_test('wabbit_wappa==0.2.0', wabbit_imports, [], [])


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
