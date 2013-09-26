# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_patchelf_installation(tmpdir):
    tmpdir.chdir()
    patchelf_versions = ['6fb4cdb']
    for ver in patchelf_versions:
        patchelf_files = ['bin/patchelf']
        perform_standard_test('patchelf==%s' % ver, [], patchelf_files)

if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
