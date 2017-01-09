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

import mock

from nova.compute import manager as compute_manager
from nova.test import TestCase
from nova_dpm.tests.unit.virt.dpm import fakeutils
from nova_dpm.tests.unit.virt.dpm import fakezhmcclient
from nova_dpm.virt.dpm import vm
from nova_dpm.virt.dpm.vm import Instance


"""
vm unit testcase
"""


def getMockInstance():
    session = fakezhmcclient.Session("hostip", "dummyhost", "dummyhost")
    client = fakezhmcclient.Client(session)
    cpc = fakezhmcclient.getFakeCPC()
    inst = Instance(fakeutils.getFakeInstance(), cpc, client)
    inst.partition = fakezhmcclient.getFakePartition()
    return inst


class VmNicTestCase(TestCase):

    def setUp(self):
        super(VmNicTestCase, self).setUp()
        vm.zhmcclient = fakezhmcclient
        self.conf = fakeutils.getFakeCPCconf()

        self.inst = getMockInstance()
        self.inst.partition.nics = fakezhmcclient.getFakeNicManager()

    @mock.patch.object(vm.LOG, 'debug')
    def test_attach_nic(self, mock_debug):

        vif1 = {'id': 1234, 'type': 'dpm_vswitch',
                'address': '12-34-56-78-9A-BC',
                'details':
                    {'object_id': '00000000-aaaa-bbbb-cccc-abcdabcdabcd'}}

        ret_val = mock.Mock()
        with mock.patch.object(fakezhmcclient.NicManager, 'create',
                               return_value=ret_val) as mock_create:
            nic_interface = self.inst.attach_nic(self.conf, vif1)
        self.assertEqual(ret_val, nic_interface)
        self.assertTrue(mock_create.called)
        call_arg_dict = mock_create.mock_calls[0][1][0]
        # Name
        self.assertTrue(call_arg_dict['name'].startswith('OpenStack'))
        self.assertIn(str(1234), call_arg_dict['name'])
        # Description
        self.assertTrue(call_arg_dict['description'].startswith('OpenStack'))
        self.assertIn('mac=12-34-56-78-9A-BC', call_arg_dict['description'])
        self.assertIn('CPCSubset=' + self.conf['cpcsubset_name'],
                      call_arg_dict['description'])
        # virtual-switch-uri
        self.assertEqual(
            '/api/virtual-switches/00000000-aaaa-bbbb-cccc-abcdabcdabcd',
            call_arg_dict['virtual-switch-uri'])


class VmHBATestCase(TestCase):

    def setUp(self):
        super(VmHBATestCase, self).setUp()
        vm.zhmcclient = fakezhmcclient
        self.conf = fakeutils.getFakeCPCconf()

        self.inst = getMockInstance()

        self.conf['physical_storage_adapter_mappings'] = \
            ["aaaaaaaa-bbbb-cccc-1123-567890abcdef:1"]
        self.inst.partition.hbas = fakezhmcclient.getFakeHbaManager()

    @mock.patch.object(vm.LOG, 'debug')
    @mock.patch.object(compute_manager.ComputeManager, '_prep_block_device',
                       return_value="blockdeviceinfo")
    def test_build_resources(self, mock_prep_block_dev, mock_debug):
        context = None
        novainstance = fakeutils.getFakeInstance()
        block_device_mapping = None
        resources = self.inst._build_resources(
            context, novainstance, block_device_mapping)
        self.assertEqual(resources['block_device_info'],
                         "blockdeviceinfo")

    @mock.patch.object(vm.LOG, 'debug')
    def test_attach_hba(self, mock_debug):
        self.inst.attachHba(self.conf)
