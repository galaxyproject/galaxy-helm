import logging
import os
import re
import yaml

from galaxy.tools import GALAXY_LIB_TOOLS_UNVERSIONED
from galaxy.jobs import JobDestination

log = logging.getLogger(__name__)

CONTAINER_RULE_MAPPER_FILE = os.path.join(
    os.path.dirname(__file__), 'container_mapper_rules.yml')


def _load_container_mappings():
    if os.path.exists(CONTAINER_RULE_MAPPER_FILE):
        with open(CONTAINER_RULE_MAPPER_FILE) as f:
            return yaml.safe_load(f)
    else:
        return {}


CONTAINER_RULE_MAP = _load_container_mappings()


def _map_resource_set(resource_set_name):
    resource_set = CONTAINER_RULE_MAP.get(
        'resources', {}).get('resource_sets', {}).get(resource_set_name)
    if resource_set:
        mapping = {
            'requests_cpu': resource_set.get(
                'requests', {}).get('cpu'),
            'requests_memory': resource_set.get(
                'requests', {}).get('memory'),
            'limits_cpu': resource_set.get(
                'limits', {}).get('cpu'),
            'limits_memory': resource_set.get(
                'limits', {}).get('memory')
        }
        # trim empty values
        return {k: v for k, v in mapping.items() if v is not None}
    else:
        raise KeyError(
            "Could not find key for resource set: {}".format(
                resource_set_name))


def _process_tool_mapping(mapping, params):
    params.update(mapping.get('container'))
    # Overwrite with user specified limits
    resource_set = mapping.get('container', {}).get('resource_set')
    if resource_set:
        params.update(_map_resource_set(resource_set))


def _apply_rule_mappings(tool, params):
    if CONTAINER_RULE_MAP:
        for mapping in CONTAINER_RULE_MAP.get('mappings', {}):
            for mapped_tool_id in mapping.get('tool_ids'):
                if re.match(mapped_tool_id, tool.id):
                    _process_tool_mapping(mapping, params)
                    return True
    return False


def _get_default_resource_set_name():
    return CONTAINER_RULE_MAP.get(
        'resources', {}).get('default_resource_set', {})


def k8s_container_mapper(tool, referrer, k8s_runner_id="k8s"):
    params = dict(referrer.params)
    params['docker_enabled'] = True
    # 1. First, apply the default resource set (if defined) as job params.
    #    These will be overridden later by individual tool mappings.
    default_resource_set_name = _get_default_resource_set_name()
    if default_resource_set_name:
        params.update(_map_resource_set(default_resource_set_name))
    # 2. Next, apply resource mappings for individual tools, overwriting the
    #    defaults.
    if not _apply_rule_mappings(tool, params):
        # 3. If no explicit rule mapping was defined, and it's a tool that
        #    requires galaxy_lib, force the default container. Otherwise,
        #    Galaxy's default container resolution will apply.
        if tool.id in GALAXY_LIB_TOOLS_UNVERSIONED:
            default_container = params.get('docker_default_container_id')
            if default_container:
                params['docker_container_id_override'] = default_container
    log.debug("[k8s_container_mapper] Dispatching to %s with params %s" % (k8s_runner_id, params))
    return JobDestination(runner=k8s_runner_id, params=params)
