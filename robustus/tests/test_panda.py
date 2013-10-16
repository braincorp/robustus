# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_panda_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()

    panda_imports = ['import panda3d',
                     'import panda3d.core',
                     'import panda3d.bullet',
                     'from panda3d.core import Mat4, TransformState',
                     'from panda3d.bullet import BulletWorld']
    panda_dependencies = ['patchelf==6fb4cdb',
                          'bullet==bc2']
    
    perform_standard_test('panda3d==bc2', panda_imports, [], panda_dependencies)


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
