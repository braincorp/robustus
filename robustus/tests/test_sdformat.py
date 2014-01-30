# ===========================================================================
#
#  COPYRIGHT 2014 Brain Corporation.
#  All rights reserved. Brain Corporation proprietary and confidential.
#
#  The party receiving this software directly from Brain Corporation
#  (the "Recipient" ) may use this software and make copies thereof as
#  reasonably necessary solely for the purposes set forth in the agreement
#  between the Recipient and Brain Corporation ( the "Agreement" ). The
#  software may be used in source code form
#  solely by the Recipient's employees. The Recipient shall have no right to
#  sublicense, assign, transfer or otherwise provide the source code to any
#  third party. Subject to the terms and conditions set forth in the Agreement,
#  this software, in binary form only, may be distributed by the Recipient to
#  its customers. Brain Corporation retains all ownership rights in and to
#  the software.
#
#  This notice shall supercede any other notices contained within the software.
# =============================================================================

import pytest
import logging
import os
from robustus.detail import perform_standard_test


def test_sdformat_installation(tmpdir):
    logging.getLogger().setLevel(logging.INFO)
    tmpdir.chdir()
    perform_standard_test('sdformat==1.4.11', [], ['lib/sdformat-1.4.11/lib/libsdformat.so'])

if __name__ == '__main__':
    pytest.main('-s %s -n0' % os.path.abspath(__file__))
