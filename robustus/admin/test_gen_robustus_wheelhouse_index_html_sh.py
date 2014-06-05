# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import sys
import logging
import os
import pytest
from robustus.detail.utility import run_shell, check_run_shell
import shutil
import subprocess


def test_gen_robustus_wheelhouse_index_html_sh(tmpdir):

    pkg_list = [
        "A_PKG-0-py27-none-any.whl",
        "B_PKG-0-py27-none-any.whl",
        "C_PKG-0-py27-none-any.whl",
        "D_PKG-0-py27-none-any.whl",
    ]

    html_expected = """\
<html>
<head><title>Index of http://thirdparty-packages.braincorporation.net/python-wheels</title></head>
<body bgcolor="white">
<h1>Index of http://thirdparty-packages.braincorporation.net/python-wheels</h1><hr><pre><a href="../">../</a>
<a href="A_PKG-0-py27-none-any.whl">A_PKG-0-py27-none-any.whl</a>
<a href="B_PKG-0-py27-none-any.whl">B_PKG-0-py27-none-any.whl</a>
<a href="C_PKG-0-py27-none-any.whl">C_PKG-0-py27-none-any.whl</a>
<a href="D_PKG-0-py27-none-any.whl">D_PKG-0-py27-none-any.whl</a>
</pre><hr></body>
</html>
"""

    command = os.path.join(os.path.dirname(__file__), "gen_robustus_wheelhouse_index_html.sh")

    work_dir = str(tmpdir.mkdir('test_gen_robustus_wheelhouse_index_html_sh'))
    os.chdir(work_dir)
    wheelhouse_dir = os.path.join(work_dir, "wheelhouse")
    os.mkdir(wheelhouse_dir)

    with pytest.raises(subprocess.CalledProcessError):
        check_run_shell(command, shell=True)

    command += " " + wheelhouse_dir
    with pytest.raises(subprocess.CalledProcessError):
        check_run_shell(command, shell=True)

    os.chdir(wheelhouse_dir)
    for pkg in pkg_list:
        with open(pkg, 'w') as f:
            f.write(pkg + '\n')
    os.chdir(work_dir)

    check_run_shell(command, shell=True)

    os.chdir(wheelhouse_dir)
    with open('index.html', 'r') as f:
        html = f.read()
    logging.info('"""' + html + '"""')
    assert html == html_expected

    os.chdir(os.path.dirname(__file__))
    shutil.rmtree(work_dir)


if __name__ == '__main__':
    test_doc_tests()
    pytest.main('-s %s -n0' % __file__)
