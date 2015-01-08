# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import pytest
from robustus.detail import perform_standard_test


def test_pyaudio_installation(tmpdir):
    tmpdir.chdir()
    exprs = ['import pyaudio']
    install_options = ['--allow-external', 'PyAudio', '--allow-unverified', 'PyAudio']
    perform_standard_test('PyAudio==0.2.8', exprs, [], [], install_options=install_options)


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
