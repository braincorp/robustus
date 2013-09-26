# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
from robustus.detail import perform_standard_test


def test_panda_installation(tmpdir):
    tmpdir.chdir()

    panda_modules = ['panda3d',
                     'panda3d.core'
                     'panda3d.bullet']

    perform_standard_test('panda3d==bc2', panda_modules, [], ['bullet==bc2'])
    # need bison to build panda 1.8.1
    if os.path.isfile('/usr/bin/bison'):
        perform_standard_test('panda3d==1.8.1', panda_modules, [], ['bullet==bc2'])


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
