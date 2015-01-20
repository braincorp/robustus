# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import os
from robustus.detail import perform_standard_test


def test_sdformat_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('sdformat==1.4.11', [], ['lib/x86_64-linux-gnu/libsdformat.so'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % os.path.abspath(__file__))
