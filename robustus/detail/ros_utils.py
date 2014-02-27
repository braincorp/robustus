# =============================================================================
# COPYRIGHT 2013 Brain Corporation.
# License under MIT license (see LICENSE file)
# =============================================================================

"""Helper utilities for ROS/ros overlays."""

import os
import hashlib


def hash_path(path, version=''):
    """Hash the path (and optionally, a version)."""
    h = hashlib.sha1()
    h.update(os.path.abspath(path))
    h.update(version)
    return h.hexdigest()
