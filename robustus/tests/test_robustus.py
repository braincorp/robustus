# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import doctest
import logging
import os
import pytest
import robustus
from robustus.detail import check_module_available
import shutil
import subprocess


def test_robustus(tmpdir):
    doctest.testmod(robustus)
    doctest.testmod(robustus.detail.utility)
    doctest.testmod(robustus.detail.requirement)

    tmpdir.chdir()
    test_env = 'test_env'

    # create env and install some packages
    logging.info('creating ' + test_env)
    robustus.execute(['env', test_env])
    assert os.path.isdir(test_env)
    assert os.path.isfile(os.path.join(test_env, '.robustus'))
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    assert os.path.isfile(robustus_executable)

    # install some packages
    logging.info('installing requirements into ' + test_env)
    subprocess.call([robustus_executable, 'install', 'pyserial'])
    test_requirements1 = 'test_requirements1.txt'
    with open(test_requirements1, 'w') as file:
        file.write('pep8==1.3.3\n')
        file.write('pytest==2.3.5\n')
    subprocess.call([robustus_executable, 'install', '-r', test_requirements1])

    # check packages are installed
    packages_to_check = ['pyserial', 'pep8==1.3.3', 'pytest==2.3.5']
    with open('freezed_requirements.txt', 'w') as req_file:
        subprocess.call([robustus_executable, 'freeze'], stdout=req_file)
    with open('freezed_requirements.txt') as req_file:
        installed_packages = [line.strip() for line in req_file]
    for package in packages_to_check:
        assert package in installed_packages

    assert check_module_available(test_env, 'serial')
    assert check_module_available(test_env, 'pep8')
    assert check_module_available(test_env, 'pytest')

    shutil.rmtree(test_env)


def test_pereditable(tmpdir):
    """Create a package with some editable requirements and check
    that perrepo runs as expected."""
    base_dir = str(tmpdir.mkdir('test_perrepo_env'))
    test_env = os.path.join(base_dir, 'env')
    working_dir = os.path.join(base_dir, 'working_dir')

    # create env and install some packages
    logging.info('creating ' + test_env)
    os.mkdir(working_dir)
    os.chdir(working_dir)
    os.system('git init .')
    robustus.execute(['env', test_env])

    os.chdir(working_dir)
    robustus_executable = os.path.join(test_env, 'bin/robustus')
    test_requirements = os.path.join(working_dir, 'requirements.txt')
    with open(test_requirements, 'w') as file:
        file.write('-e git+https://github.com/braincorp/python-ardrone.git@master#egg=ardrone\n')

    subprocess.call([robustus_executable, 'install', '-r', test_requirements])

    # Now check that robustus behaves as expected
    subprocess.call([robustus_executable, 'perrepo', 'touch', 'foo'])
    assert os.path.exists(os.path.join(working_dir, 'foo'))
    assert os.path.exists(os.path.join(test_env, 'src', 'ardrone', 'foo'))


if __name__ == '__main__':
    pytest.main('-s %s -n0' % __file__)
