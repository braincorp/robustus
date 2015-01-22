# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import os
from robustus.detail import perform_standard_test


@pytest.mark.skipif("'TRAVIS' in os.environ",
                    reason="travis doesn't have access to brainos_core")
def test_brainos_core_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('brainos_core==develop', ['import brainos2'], ['bin/brainosd'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % os.path.abspath(__file__))
