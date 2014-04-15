# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_pygst_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    files = []
    imports = ['import pygtk', 'import gtk', 'import pygst', 'import gst']
    dependencies = ['PyGObject', 'PyGTK']
    perform_standard_test('PyGST==0.10', imports, files, dependencies)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
