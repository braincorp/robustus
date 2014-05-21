# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


# Simplest test to check basic functionality for manual use
@pytest.mark.skipif("'TRAVIS' in os.environ",
                    reason="there are enough autotests already")
def test_pep8_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('pep8', ['import pep8'], [], [])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
