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


"""
Host will have the handle to the CPCSubsetMgr which will retrieve cpcsubsets
"""

from nova.i18n import _LW
from nova.objects import fields as obj_fields
from oslo_log import log as logging
from oslo_serialization import jsonutils


LOG = logging.getLogger(__name__)

zhmcclient = None


class Host(object):

    def __init__(self, conf, cpc, client):

        LOG.warning(_LW('Host initializing for host %(hostname)s'),
                    {'hostname': cpc.properties['name']})

        self._conf = conf
        self._client = client
        self._cpc = cpc
        self._instances = []
        self._properties = self._get_host_poperties()

        LOG.warning(_LW('Host initializing done'))

    @property
    def properties(self):
        LOG.warning(_LW('properties'))
        self._properties = self._get_host_poperties()
        return self._properties

    def _get_host_poperties(self):
        LOG.warning(_LW('_get_host_properties'))
        dict_mo = {
            "memory_mb": self._conf["max_memory_mb"],
            "vcpus": self._conf["max_processors"],
            'vcpus_used': self._get_proc_used(),
            "local_gb": 1024, '''TODO:Update with relevant value'''
            "memory_mb_used": self._get_mem_used(),
            "local_gb_used": 0, '''TODO:Update with relevant value'''
            "cpu_info": self._get_cpu_info(self._conf["max_processors"]),
            "hypervisor_type": "PRSM",
            "hypervisor_version": 1000,
            "numa_topology": "",
            "hypervisor_hostname": self._conf['hostname'],
            "dpm_name": self._cpc.properties['name'],
            "disk_available_least": 1024,
            'supported_instances':
            [("s390", obj_fields.HVType.BAREMETAL, obj_fields.VMMode.HVM)]}
        '''TODO BareMETAL will be updated with PRSM after HVType updated in
         upstream code'''

        LOG.warning(dict_mo)

        return dict_mo

    def _get_cpu_info(self, cores):
        """Get cpuinfo information.

        Obtains cpu feature from virConnect.getCapabilities,
        and returns as a json string.

        :return: see above description

        """
        cpu_info = dict()
        cpu_info['arch'] = 's390x'
        cpu_info['model'] = 'host'
        cpu_info['vendor'] = 'IBM'
        topology = dict()
        topology['sockets'] = 1
        topology['cores'] = cores
        topology['threads'] = 1
        cpu_info['topology'] = topology

        features = list()
        cpu_info['features'] = features
        return jsonutils.dumps(cpu_info)

    def _get_proc_used(self):
        return 0

    def _get_mem_used(self):
        return 0
