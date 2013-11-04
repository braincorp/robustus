# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

import logging
import os
import platform
import subprocess
import shutil
import sys
from utility import cp, unpack, safe_remove
from requirement import RequirementException


def install(robustus, requirement_specifier, rob_file, ignore_index):
    
    print 'HELLO I AM INSTALLING BOOST FROM THIS FILE!'
    
    boost_install_dir = os.path.join(robustus.cache, 'boost-python-%s' % requirement_specifier.version)
    
    def in_cache():
        return False
        #return os.path.isfile(os.path.join(boost_install_dir, 'pygame/__init__.py'))

    if not in_cache() and not ignore_index:
        # http://downloads.sourceforge.net/project/boost/boost/1.55.0.beta.1/boost_1_55_0b1.tar.bz2
        # PYPI index is broken for pygame, download manually
        logging.info('Downloading boost')
        #if requirement_specifier.version == '1.9.1':
            #pygame_archive_name = 'pygame-1.9.1release'
            #pygame_tgz = pygame_archive_name + '.tar.gz'
        boost_tgz = 'boost_1_55_0b1.tar.bz2'
        url = 'http://downloads.sourceforge.net/project/boost/boost/1.55.0.beta.1/' + boost_tgz
        
        subprocess.call(['wget', '-c', url, '-O', boost_tgz])
        
        logging.info('Unpacking boost')
        unpack(boost_tgz)
    
    # get boost
    #Download boost_1_54_0.tar.bz2.
    #In the directory where you want to put the Boost installation, execute
    #tar --bzip2 -xf /path/to/boost_1_54_0.tar.bz2
        
    # get bjam build driver
    
    # cd into the libs/python/example/quickstart/ directory of your Boost installation, which contains a small example project.
    # Invoke bjam.
    # ~/boost_1_34_0/É/quickstart$ bjam toolset=gcc --verbose-test test

