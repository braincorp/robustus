# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import doctest
import logging
import os
import pytest
import robustus
import shutil
import subprocess


def test_robustus():
    cwd = os.getcwd()
    test_env = 'test_env'
    if os.path.isdir(test_env):
        shutil.rmtree(test_env)

    # create env and install some packages
    logging.info('creating ' + test_env)
    robustus.execute(['env', test_env])
    assert os.path.isdir(test_env)
    os.chdir(test_env)
    assert os.path.isfile('.robustus')
    assert os.path.isfile('bin/robustus')

    # install some packages
    logging.info('installing requirements into ' + test_env)
    subprocess.call(['bin/robustus', 'install', 'pyserial'])
    test_requirements1 = 'test_requirements1.txt'
    with open(test_requirements1, 'w') as file:
        file.write('pep8==1.3.3\n')
        file.write('pytest==2.3.5\n')
    subprocess.call(['bin/robustus', 'install', '-r', test_requirements1])
    test_requirements2 = 'test_requirements2.txt'

    # check packages are installed
    packages_to_check = ['pyserial', 'pep8==1.3.3', 'pytest==2.3.5']
    with open('freezed_requirements.txt', 'w') as req_file:
        subprocess.call(['bin/robustus', 'freeze'], stdout=req_file)
    with open('freezed_requirements.txt') as req_file:
        installed_packages = [line.strip() for line in req_file]
    for package in packages_to_check:
        assert package in installed_packages

    os.chdir(cwd)
    shutil.rmtree(test_env)

if __name__ == '__main__':
    doctest.testmod(robustus)
    doctest.testmod(robustus.detail.utility)
    doctest.testmod(robustus.detail.requirement)
    pytest.main('-s %s -n0' % __file__)
