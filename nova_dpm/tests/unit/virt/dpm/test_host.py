# Copyright 2016 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import mock

from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakecpcs
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import host


"""
cpcsubset unit testcase
"""


def fakeHost():
    session = fakezhmcclient.Session("dummy", "dummy",
                                     "dummy")
    client = fakezhmcclient.Client(session)

    cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
    cpc = fakecpcs.getFakeCPC(cpcmanager)
    conf = fakecpcs.getFakeCPCconf()

    host1 = host.Host(conf, cpc, client)
    return host1


class HostTestCase(TestCase):

    def setUp(self):
        super(HostTestCase, self).setUp()
        self._session = fakezhmcclient.Session(
            "dummy", "dummy", "dummy")

    @mock.patch.object(host.LOG, 'debug')
    def test_host(self, mock_warning):

        client = fakezhmcclient.Client(self._session)

        cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
        cpc = fakecpcs.getFakeCPC(cpcmanager)
        conf = fakecpcs.getFakeCPCconf()

        host.Host(conf, cpc, client)

        expected_arg = "Host initializing done"
        assertlogs = False
        for call in mock_warning.call_args_list:
            if (len(call) > 0):
                if (len(call[0]) > 0 and call[0][0] == expected_arg):
                    assertlogs = True

        self.assertTrue(assertlogs)

    @mock.patch.object(host.LOG, 'debug')
    def test_host_properties(self, mock_warning):

        client = fakezhmcclient.Client(self._session)

        cpcmanager = fakezhmcclient.getCpcmgrForClient(client)
        cpc = fakecpcs.getFakeCPC(cpcmanager)
        conf = fakecpcs.getFakeCPCconf()

        host1 = host.Host(conf, cpc, client)
        host_properties = host1.properties
        self.assertEqual(host_properties['hypervisor_hostname'],
                         'S12subset')
        self.assertEqual(host_properties['cpc_name'], 'fakecpc')
        cpu_info = host_properties['cpu_info']
        cpu_info_dict = json.loads(cpu_info)
        self.assertEqual(cpu_info_dict['arch'], 's390x')
        self.assertEqual(cpu_info_dict['vendor'], 'IBM')
