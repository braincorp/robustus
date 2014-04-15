# =============================================================================
# COPYRIGHT 2014 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
import logging
from robustus.detail import perform_standard_test


def test_pocketsphinx_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    files = ['lib/libsphinxbase.so']
    imports = ['import wrap_pocketsphinx']
    dependencies = ['patchelf==6fb4cdb', 'cython==0.20.1', 'sphinxbase==0.8']
    perform_standard_test('pocketsphinx==0.8', imports, files, dependencies)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
