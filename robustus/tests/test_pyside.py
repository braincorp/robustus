# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import os
import pytest
import logging
from robustus.detail import perform_standard_test


@pytest.mark.skipif("'TRAVIS' in os.environ",
                    reason="pyside compilation takes more than 50 mins, so we can't test it on travis")
def test_pyside_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    imports = ['import PySide',
               'from PySide import QtGui']
    perform_standard_test('PySide==1.2.1', imports)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
