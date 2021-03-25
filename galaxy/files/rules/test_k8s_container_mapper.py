import sys
import unittest
import yaml

import k8s_container_mapper


class ContainerMapperTest(unittest.TestCase):

    _multiprocess_can_split_ = True

    class Tool:
        def __init__(self, tool_id):
            self.id = tool_id

    class Referrer:
        def __init__(self):
            self.params = {}

    def patch_mapper(self, rule_map):
        k8s_container_mapper.CONTAINER_RULE_MAP = yaml.safe_load(rule_map)

    def test_existing_tool_map_small_works(self):
        RULE_MAP_SMALL_OLD = '''
          mappings:
            - tool_ids:
                - sort1
                - Grouping1
              container:
                docker_container_id_override: test_container
                resource_set: small
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
            default_resource_set: small
        '''

        self.patch_mapper(RULE_MAP_SMALL_OLD)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('sort1'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
        assert (destination.params.get(
            'requests_cpu') == 1)
        assert (destination.params.get(
            'requests_memory') == '500m')
        assert (destination.params.get(
            'limits_cpu') == 2)
        assert (destination.params.get(
            'limits_memory') == '1G')

        RULE_MAP_SMALL = '''
          mappings:
            set_small:
              tool_ids:
                - sort1
                - Grouping1
              docker_container_id_override: test_container
              resource_set: small
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
            default_resource_set: small
        '''

        self.patch_mapper(RULE_MAP_SMALL)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('sort1'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
        assert (destination.params.get(
            'requests_cpu') == 1)
        assert (destination.params.get(
            'requests_memory') == '500m')
        assert (destination.params.get(
            'limits_cpu') == 2)
        assert (destination.params.get(
            'limits_memory') == '1G')

    def test_existing_tool_map_medium_works(self):
        RULE_MAP_MEDIUM_OLD = '''
          mappings:
            - tool_ids:
                - sort1
                - Grouping1
              container:
                docker_container_id_override: test_container
                resource_set: medium_mem
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
              medium_mem:
                requests:
                  memory: 1G
                limits:
                  memory: 2G
            default_resource_set: small
        '''

        self.patch_mapper(RULE_MAP_MEDIUM_OLD)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('Grouping1'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
        assert (destination.params.get(
            'requests_cpu') == 1)
        assert (destination.params.get(
            'requests_memory') == '1G')
        assert (destination.params.get(
            'limits_cpu') == 2)
        assert (destination.params.get(
            'limits_memory') == '2G')

        RULE_MAP_MEDIUM = '''
          mappings:
              tool_ids:
                - sort1
                - Grouping1
              docker_container_id_override: test_container
              resource_set: medium_mem
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
              medium_mem:
                requests:
                  memory: 1G
                limits:
                  memory: 2G
            default_resource_set: small
        '''

        self.patch_mapper(RULE_MAP_MEDIUM)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('Grouping1'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
        assert (destination.params.get(
            'requests_cpu') == 1)
        assert (destination.params.get(
            'requests_memory') == '1G')
        assert (destination.params.get(
            'limits_cpu') == 2)
        assert (destination.params.get(
            'limits_memory') == '2G')

    def test_nonexisting_tool_resource(self):
        RULE_MAP_RESOURCE_NOTEXIST = '''
          mappings:
            non_existent:
              tool_ids:
                - sort1
                - Grouping1
              docker_container_id_override: test_container
              resource_set: non_existent
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
              medium_mem:
                requests:
                  memory: 1G
                limits:
                  memory: 2G
            default_resource_set: small
        '''
        self.patch_mapper(RULE_MAP_RESOURCE_NOTEXIST)

        if sys.version_info < (3, 1):
            assertRegex = self.assertRaisesRegexp
        else:
            assertRegex = self.assertRaisesRegex
        with assertRegex(KeyError, 'non_existent'):
            k8s_container_mapper.k8s_container_mapper(
                ContainerMapperTest.Tool('Grouping1'),
                ContainerMapperTest.Referrer())

    def test_nonexisting_tool(self):
        RULE_MAP_TOOL_NOTEXIST = '''
          mappings:
            non_existent:
              tool_ids:
                - sort1
                - Grouping1
              docker_container_id_override: test_container
              resource_set: non_existent
          resources:
            resource_sets:
              small:
                requests:
                  cpu: 1
                  memory: 500m
                limits:
                  cpu: 2
                  memory: 1G
              medium_mem:
                requests:
                  memory: 1G
                limits:
                  memory: 2G
            default_resource_set: small
        '''
        self.patch_mapper(RULE_MAP_TOOL_NOTEXIST)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('UnknownTool'),
            ContainerMapperTest.Referrer())
        assert 'docker_container_id_override' not in destination.params
        # Should have default resource mappings
        assert (destination.params.get(
            'requests_cpu') == 1)
        assert (destination.params.get(
            'requests_memory') == '500m')
        assert (destination.params.get(
            'limits_cpu') == 2)
        assert (destination.params.get(
            'limits_memory') == '1G')

    def test_no_resource_mappings(self):
        RULE_MAP_NO_RESOURCES_OLD = '''
          mappings:
            - tool_ids:
                - sort1
                - Grouping1
              container:
                docker_container_id_override: test_container
        '''
        self.patch_mapper(RULE_MAP_NO_RESOURCES_OLD)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('sort1'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')

    def test_regex_mappings(self):
        RULE_MAP_REGEX = '''
          mappings:
            regex:
              tool_ids:
                - .*data_manager_sam_fasta_index_builder/sam_fasta_index_builder/.*
              docker_container_id_override: test_container
        '''
        self.patch_mapper(RULE_MAP_REGEX)

        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool('toolshed.g2.bx.psu.edu/repos/devteam/data_manager_sam_fasta'
                '_index_builder/sam_fasta_index_builder/0.0.3'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
        destination = k8s_container_mapper.k8s_container_mapper(
            ContainerMapperTest.Tool(
                'toolshed.g2.bx.psu.edu/repos/devteam/data_manager_sam_fasta'
                '_index_builder/sam_fasta_index_builder/0.0.4'),
            ContainerMapperTest.Referrer())
        assert(destination.params.get(
            'docker_container_id_override') == 'test_container')
