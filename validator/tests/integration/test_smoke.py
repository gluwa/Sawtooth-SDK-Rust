# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import traceback
import unittest
import os
import logging

from txnintegration.integer_key_load_cli import IntKeyLoadTest
from txnintegration.simcontroller import get_default_sim_controller
from txnintegration.utils import is_convergent

logger = logging.getLogger(__name__)

ENABLE_INTEGRATION_TESTS = True \
    if os.environ.get("ENABLE_INTEGRATION_TESTS", False) == "1" else False


class TestSmoke(unittest.TestCase):
    def _run_int_load(self, num_nodes, archive_name, overrides):
        """
        Args:
            num_nodes (int): Total number of nodes in network simulation
            archive_name (str): Name for tarball summary of test results
        """,
        sim = None
        try:
            test = IntKeyLoadTest()
            if "TEST_VALIDATOR_URLS" not in os.environ:
                print "Launching validator network."
                sim = get_default_sim_controller(num_nodes,
                                                 overrides=overrides)
                sim.do_genesis()
                sim.launch()
                urls = sim.urls()
            else:
                print "Fetching Urls of Running Validators"
                # TEST_VALIDATORS_RUNNING is a list of validators urls
                # separated by commas.
                # e.g. 'http://localhost:8800,http://localhost:8801'
                urls = str(os.environ["TEST_VALIDATOR_URLS"]).split(",")
            print "Testing transaction load."
            test.setup(urls, 100)
            test.run(2)
            test.validate()
            self.assertTrue(is_convergent(urls, tolerance=2, standard=5))
        finally:
            if sim is not None:
                sim.shutdown(archive_name=archive_name)
            else:
                print "No Validator data and logs to preserve"

    @unittest.skipUnless(ENABLE_INTEGRATION_TESTS, "integration test")
    def test_intkey_load_poet0(self):
        overrides = {}
        self._run_int_load(5, "TestSmokeResultsPoet0", overrides)

    @unittest.skipUnless(ENABLE_INTEGRATION_TESTS, "integration test")
    def test_intkey_load_dev_mode(self):
        overrides = {'LedgerType': 'dev_mode'}
        self._run_int_load(1, "TestSmokeResultsDevMode", overrides)
