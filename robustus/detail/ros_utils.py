# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

"""Helper utilities for ROS/ros overlays."""

import os
import hashlib


def hash_path(path, version='', ros_install_path=''):
    """Hash a path (and optionally, a version and/or ros_install_path)."""
    h = hashlib.sha1()
    h.update(os.path.abspath(path))
    h.update(version)
    if ros_install_path != '':
        h.update(os.path.abspath(ros_install_path))
    return h.hexdigest()
