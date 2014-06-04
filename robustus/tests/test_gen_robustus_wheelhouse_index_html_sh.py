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
        "Flask-0.10-py27-none-any.whl",
        "Jinja2-2.7.2-py27-none-any.whl",
        "MarkupSafe-0.23-cp27-none-linux_armv7l.whl",
        "Werkzeug-0.9.4-py27-none-any.whl",
        "itsdangerous-0.24-py27-none-any.whl"
    ]

    html_expected = """\
<html>
<head><title>Index of http://thirdparty-packages.braincorporation.net/python-wheels</title></head>
<body bgcolor="white">
<h1>Index of http://thirdparty-packages.braincorporation.net/python-wheels</h1><hr><pre><a href="../">../</a>
<a href="Flask-0.10-py27-none-any.whl">Flask-0.10-py27-none-any.whl</a>
<a href="Jinja2-2.7.2-py27-none-any.whl">Jinja2-2.7.2-py27-none-any.whl</a>
<a href="MarkupSafe-0.23-cp27-none-linux_armv7l.whl">MarkupSafe-0.23-cp27-none-linux_armv7l.whl</a>
<a href="Werkzeug-0.9.4-py27-none-any.whl">Werkzeug-0.9.4-py27-none-any.whl</a>
<a href="itsdangerous-0.24-py27-none-any.whl">itsdangerous-0.24-py27-none-any.whl</a>
</pre><hr></body>
</html>
"""

    cwd = os.getcwd()
    print "cwd = \"" + cwd + "\""
    command = os.path.join(cwd, "../admin/gen_robustus_wheelhouse_index_html.sh")

    work_dir = str(tmpdir.mkdir('test_gen_robustus_wheelhouse_index_html_sh'))
    os.chdir(work_dir)
    wheelhouse_dir = "wheelhouse"
    os.mkdir(wheelhouse_dir)

    try:
        exception_occurred = False
        check_run_shell(command, shell=True)
    except subprocess.CalledProcessError as e:
        exception_occurred = True
    assert exception_occurred

    command += " ./" + wheelhouse_dir
    try:
        exception_occurred = False
        check_run_shell(command, shell=True)
    except subprocess.CalledProcessError as e:
        exception_occurred = True
    assert exception_occurred

    os.chdir(wheelhouse_dir)
    for pkg in pkg_list:
        with open(pkg, 'w') as f:
            f.write(pkg + '\n')
    os.chdir(work_dir)

    try:
        exception_occurred = False
        check_run_shell(command, shell=True)
    except subprocess.CalledProcessError as e:
        exception_occurred = True
    assert not exception_occurred

    os.chdir(wheelhouse_dir)
    with open('index.html', 'r') as f:
        html=f.read()
    assert html == html_expected

    os.chdir(cwd)
    shutil.rmtree(work_dir)


if __name__ == '__main__':
    test_doc_tests()
    pytest.main('-s %s -n0' % __file__)
