# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

from setuptools import setup
import robustus


setup(name='robustus',
      author='Brain Corporation',
      author_email='trifonov@braincorporation.com',
      url='https://github.com/braincorp/roboenv',
      long_description='Tool to make and configure python virtualenv, setup necessary packages and cache them if necessary.',
      version=robustus.__version__,
      packages=['robustus', 'robustus.detail'],
      scripts=['bin/robustus'])
