# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import subprocess
import sys


def install(robustus, requirement_specifier, rob_file):
    cudamat_install_dir = os.path.join(robustus.cache, 'cudamat')
    if not os.path.isdir(cudamat_install_dir):
        logging.info('Downloading cudamat')
        cwd = os.getcwd()
        url = 'https://s3.amazonaws.com/thirdparty-packages.braincorporation.net/cudamat-01-15-2010.tar.gz'
        subprocess.call(['wget', '-c', url, '-P', robustus.cache])

        logging.info('Unpacking cudamat')
        os.chdir(robustus.cache)
        cudamat_tar = 'cudamat-01-15-2010.tar.gz'
        subprocess.call(['tar', 'xzvf', cudamat_tar])

        logging.info('Building cudamat')
        os.chdir(cudamat_install_dir)
        subprocess.call(['make'])
        os.chdir(cwd)

    python_dir = os.path.join(os.path.dirname(sys.executable), os.path.pardir)
    cudamat_python_dir = os.path.join(python_dir, 'lib/python2.7/site-packages/cudamat')
    if not os.path.islink(cudamat_python_dir):
        logging.info('Linking cudamat to virtualenv')
        # this may seem a bit freakish to patch library search path directly in python source,
        # but this most robust solution I've found
        cudamat_py = os.path.join(cudamat_install_dir, 'cudamat.py')
        cudamat_so = os.path.join(cudamat_install_dir, 'libcudamat.so')
        cudamat_py_source = open(cudamat_py).read()
        with open(cudamat_py, 'w') as f:
            f.write(cudamat_py_source.replace('libcudamat.so', cudamat_so))
        os.symlink(cudamat_install_dir, cudamat_python_dir)
