"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers.manila_service_verify import TestPluginCheck
from helpers import plugin
from proboscis import test


@test(groups=['manila_plugin', 'manila_integration'])
class TestManilaIntegration(TestBasic):
    """Integration test suite.

    The goal of integration testing is to ensure that Fuel Manila plugin work
    on cluster with different sets of roles, nodes, storage backends types
    will be used by QA to accept software builds from Development team.

    """

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["manila_share_ha"])
    @log_snapshot_after_test
    def manila_share_ha(self):
        """Check cluster deploy with Manila Plugin and two Manila-share roles.

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with VLAN segmentation
                * Block Storage: LVM
                * Other Storages: default
                * Additional services: disabled
            3. Enable plugin and add nodes with following roles:
                * Controller + Manila-share
                * Compute + Manila-share
                * Cinder + Manila-data
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).
        """

        self.env.revert_snapshot("ready_with_3_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={"net_provider": 'neutron'}
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller', 'manila-share'],
             'slave-02': ['compute', 'manila-share'],
             'slave-03': ['cinder', 'manila-data']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id,check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])

        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["manila_data_ha"])
    @log_snapshot_after_test
    def manila_data_ha(self):
        """Check cluster deploy with Manila Plugin and two Manila-data roles.

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with tunneling segmentation
                * Block Storage: LVM
                * Other Storages: default
                * Additional services: disabled
            3. Enable plugin and add nodes with following roles:
                * Controller + Manila-data
                * Compute + Manila-data
                * Cinder + Manila-share
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).
        """

        self.env.revert_snapshot("ready_with_3_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": 'tun'
            }
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller', 'manila-data'],
             'slave-02': ['compute', 'manila-data'],
             'slave-03': ['cinder', 'manila-share']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id,check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])

        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["manila_with_ceilometer"])
    @log_snapshot_after_test
    def manila_with_ceilometer(self):
        """Deploy a cluster with additional component Ceilometer

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with tunneling segmentation
                * Additional services: Ceilometer
            3. Enable plugin and add nodes with following roles:
                * Controller + Mongo-DB
                * Mongo-DB + Manila-data + Manila-share
                * Cinder + Mongo-DB
                * Compute
                * Compute
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).

        """

        self.env.revert_snapshot("ready_with_5_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={
                'ceilometer': True
            }
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller', 'mongo'],
             'slave-02': ['mongo', 'manila-data', 'manila-share'],
             'slave-03': ['cinder', 'mongo'],
             'slave-04': ['compute'],
             'slave-05': ['compute']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id,check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               timeout=60*60,
                               test_sets=['smoke', 'sanity','tests_platform'])
        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["manila_with_murano"])
    @log_snapshot_after_test
    def manila_with_murano(self):
        """Deploy a cluster with additional component Murano

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with VLAN segmentation
                * Additional services: Murano
            3. Enable plugin and add nodes with following roles:
                * Controller
                * Compute + Manila-share
                * Cinder + Manila-data
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).

        """

        self.env.revert_snapshot("ready_with_3_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={
                'murano': True
            }
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute', 'manila-share'],
             'slave-03': ['cinder', 'manila-data']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])

        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["manila_with_sahara"])
    @log_snapshot_after_test
    def manila_with_sahara(self):
        """Deploy a cluster with additional component Sahara

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with tunneling segmentation
                * Additional services: Sahara
            3. Enable plugin and add nodes with following roles:
                * Controller
                * Compute + Manila-share
                * Cinder + Manila-data
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).

        """

        self.env.revert_snapshot("ready_with_3_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={
                'net_provider': 'neutron',
                'net_segment_type': 'tun',
                'sahara': True
            }
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {
             'slave-01': ['controller'],
             'slave-02': ['compute', 'manila-data'],
             'slave-03': ['cinder', 'manila-share']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])

        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["manila_cinder_ceph"])
    @log_snapshot_after_test
    def manila_cinder_ceph(self):
        """Deploy a cluster using both Ceph and Cinder backends.

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with tunneling segmentation
                * Block Storage: LVM
                * Image Storage: Ceph
                * Additional services: disabled
            3. Enable plugin and add nodes with following roles:
                * Controller + Cinder + Ceph-OSD
                * Controller + Cinder + Manila-data
                * Controller + Ceph-OSD
                * Compute + Cinder
                * Ceph-OSD + Cinder + Compute + Manila-share
            4. Deploy cluster with plugin.
            5. Run OSTF
            6. Verify Manila service basic functionality (share create/mount).
        """

        self.env.revert_snapshot("ready_with_5_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={
                'net_provider': 'neutron',
                'net_segment_type': 'tun',
                'images_ceph': True
            }
        )

        self.show_step(3)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller', 'cinder', 'ceph-osd'],
                'slave-02': ['controller', 'cinder', 'manila-data'],
                'slave-03': ['controller', 'ceph-osd'],
                'slave-04': ['compute', 'cinder'],
                'slave-05': ['ceph-osd', 'cinder', 'compute', 'manila-share'],
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity', 'ha'])

        self.show_step(6)
        TestPluginCheck(self).verify_manila_functionality()

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["manila_enable_after_deploy"])
    @log_snapshot_after_test
    def manila_enable_after_deploy(self):
        """Check cluster deploy with Manila Plugin added after deploy.

        Scenario:
            1. Upload plugins and install.
            2. Create environment :
                * Networking: Neutron with VLAN segmentation
                * Block Storage: LVM
                * Other Storages: default
                * Additional services: disabled
            3. Disable plugin and add nodes with following roles:
                * Controller
                * Compute + Cinder
            4. Deploy cluster without plugin.
            5. Run OSTF
            6. Enable plugin and add one more node
                * Manila-share + Manila-data
            7. Deploy cluster with plugin.
            8. Run OSTF
            9. Verify Manila service basic functionality (share create/mount).
        """

        self.env.revert_snapshot("ready_with_3_slaves")
        self.show_step(1)
        plugin.install_manila_plugin(self.ssh_manager.admin_ip)
        plugin.upload_manila_image(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            settings={}
        )

        self.show_step(3)
        plugin.disable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute', 'cinder']
             }
        )

        self.show_step(4)
        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.show_step(5)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])
        self.show_step(6)
        plugin.enable_plugin_manila(cluster_id, self.fuel_web)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-03': ['manila-share', 'manila-data']}
        )
        self.show_step(7)
        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.show_step(8)
        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               test_sets=['smoke', 'sanity'])
        self.show_step(9)
        TestPluginCheck(self).verify_manila_functionality()

