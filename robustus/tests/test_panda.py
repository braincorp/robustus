# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
from robustus.detail import perform_standard_test


def test_panda_installation(tmpdir):
    tmpdir.chdir()
    perform_standard_test('panda3d==bc1', ['panda3d'], [], ['bullet==bc1'])
    # need bison to build panda 1.8.1
    if os.path.isfile('/usr/bin/bison'):
        perform_standard_test('panda3d==1.8.1', ['panda3d'], [], ['bullet==bc1'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
