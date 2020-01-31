"""
Switch to the Galaxy application folder (not the Galaxy Helm chart foler),
activate Galaxy venv, and run ``nosetests -v /path/to/galaxy-helm/files/rules/``
to run all the unit tests.

To run a single test, use the following syntax:
``nosetests -v --nocapture /path/to/galaxy-helm/files/rules/test_k8s_container_mapper.py:ContainerMapperTest.test_existing_tool_map_small_works``
"""
