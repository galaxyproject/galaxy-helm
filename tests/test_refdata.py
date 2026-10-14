"""Check reference-data access in rendered application and job configuration.

Run with: python -m unittest discover -s tests -v (requires Helm and PyYAML).
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

CHART = Path(__file__).resolve().parents[1] / "galaxy"
IDC = "idc.galaxyproject.org"
DATA = "data.galaxyproject.org"


def render(overrides=None):
    with tempfile.TemporaryDirectory() as directory:
        values = Path(directory) / "values.yaml"
        values.write_text(yaml.safe_dump(overrides or {}))
        output = subprocess.check_output(
            ["helm", "template", "reference-test", str(CHART), "-n", "galaxy", "-f", str(values)],
            text=True,
        )
    return [document for document in yaml.safe_load_all(output) if document]


def configurations(documents):
    document = next(d for d in documents if d["metadata"]["name"].endswith("-configs"))
    contents = document.get("data", document.get("stringData"))
    return yaml.safe_load(contents["galaxy.yml"])["galaxy"], yaml.safe_load(contents["job_conf.yml"])


def reference_containers(documents):
    for document in documents:
        if document["kind"] not in ("Deployment", "Job"):
            continue
        pod = document["spec"]["template"]["spec"]
        for container in pod.get("containers", []) + pod.get("initContainers", []):
            if any(mount["name"] == "refdata-gxy" for mount in container.get("volumeMounts", [])):
                yield document["metadata"]["name"], container


class ReferenceDataTests(unittest.TestCase):
    def assert_repositories(self, documents, expected):
        containers = list(reference_containers(documents))
        self.assertTrue(containers)
        for name, container in containers:
            with self.subTest(pod=name, container=container["name"]):
                mounts = {m["mountPath"]: m for m in container["volumeMounts"] if m["name"] == "refdata-gxy"}
                self.assertEqual(set(mounts), {f"/cvmfs/{repo}" for repo in expected})
                for repository in expected:
                    mount = mounts[f"/cvmfs/{repository}"]
                    self.assertEqual(mount["subPath"], repository)
                    self.assertEqual(mount["mountPropagation"], "HostToContainer")
                    if repository != DATA:
                        self.assertTrue(mount["readOnly"])
        galaxy, jobs = configurations(documents)
        claims = jobs["runners"]["k8s"]["k8s_persistent_volume_claims"].split(",")
        for repository in expected:
            self.assertIn(
                f"reference-test-galaxy-refdata-gxy-pvc/{repository}:/cvmfs/{repository}:r", claims
            )
        reference_claims = [
            d for d in documents
            if d["kind"] == "PersistentVolumeClaim" and "refdata" in d["metadata"]["name"]
        ]
        self.assertEqual(len(reference_claims), 1)
        return galaxy, jobs

    def test_defaults_reach_all_galaxy_processes_and_setup_containers(self):
        documents = render()
        galaxy, _ = self.assert_repositories(documents, [DATA, IDC])
        names = {name for name, _ in reference_containers(documents)}
        expected_deployments = {
            "reference-test-galaxy-web", "reference-test-galaxy-job-0",
            "reference-test-galaxy-workflow", "reference-test-galaxy-celery",
            "reference-test-galaxy-celery-beat",
        }
        self.assertTrue(expected_deployments.issubset(names))
        setup_containers = {
            container["name"] for name, container in reference_containers(documents)
            if "-init-" in name
        }
        self.assertEqual(setup_containers, {
            "galaxy-init-db", "galaxy-init-tool-data", "galaxy-init-mounts",
        })
        paths = galaxy["tool_data_table_config_path"].split(",")
        self.assertEqual(paths, [
            "/galaxy/server/config/mutable/shed_tool_data_table_conf.xml",
            f"/cvmfs/{DATA}/managed/location/tool_data_table_conf.xml",
            f"/cvmfs/{DATA}/byhand/location/tool_data_table_conf.xml",
            f"/cvmfs/{IDC}/config/tool_data_table_conf.xml",
        ])
        self.assertEqual(galaxy["builds_file_path"], f"/cvmfs/{DATA}/managed/location/builds.txt")
        self.assertEqual(galaxy["len_file_path"], f"/cvmfs/{DATA}/managed/len/ucsc")

    def test_disabling_idc_removes_mounts_and_configuration(self):
        documents = render({"refdata": {"cvmfsAdditionalRepositories": {IDC: {"enabled": False}}}})
        galaxy, jobs = self.assert_repositories(documents, [DATA])
        self.assertNotIn(IDC, galaxy["tool_data_table_config_path"])
        self.assertNotIn(IDC, jobs["runners"]["k8s"]["k8s_persistent_volume_claims"])

    def test_additional_repository_and_custom_runner_share_configuration(self):
        repository = "example.galaxyproject.org"
        documents = render({
            "refdata": {"cvmfsAdditionalRepositories": {repository: {"enabled": True, "toolDataTableConfigPaths": ["config/example.xml"]}}},
            "configs": {"job_conf.yml": {"runners": {"remote": {"docker_extra_volumes": '{{ include "galaxy.refdata_container_volumes" . }}'}}}},
        })
        galaxy, jobs = self.assert_repositories(documents, [DATA, IDC, repository])
        self.assertIn(f"/cvmfs/{repository}/config/example.xml", galaxy["tool_data_table_config_path"].split(","))
        self.assertEqual(set(jobs["runners"]["remote"]["docker_extra_volumes"].split(",")), {f"/cvmfs/{repo}:/cvmfs/{repo}:ro" for repo in [DATA, IDC, repository]})

    def test_disabled_reference_data_has_no_mounts_or_table_paths(self):
        documents = render({"refdata": {"enabled": False}})
        self.assertEqual(list(reference_containers(documents)), [])
        galaxy, jobs = configurations(documents)
        self.assertEqual(galaxy["tool_data_table_config_path"], "/galaxy/server/config/mutable/shed_tool_data_table_conf.xml")
        self.assertNotIn("refdata-gxy-pvc", jobs["runners"]["k8s"]["k8s_persistent_volume_claims"])

    def test_s3_preserves_legacy_mount_without_idc(self):
        documents = render({"refdata": {"type": "s3csi"}})
        for _, container in reference_containers(documents):
            mounts = [m for m in container["volumeMounts"] if m["name"] == "refdata-gxy"]
            self.assertEqual(mounts, [{"name": "refdata-gxy", "mountPath": f"/cvmfs/{DATA}"}])
        galaxy, jobs = configurations(documents)
        self.assertNotIn(IDC, galaxy["tool_data_table_config_path"])
        self.assertIn(f"reference-test-galaxy-refdata-gxy-pvc:/cvmfs/{DATA}:r", jobs["runners"]["k8s"]["k8s_persistent_volume_claims"].split(","))

    def test_secret_configuration_and_multiple_job_handlers(self):
        documents = render({"useSecretConfigs": True, "jobHandlers": {"replicaCount": 2}})
        self.assert_repositories(documents, [DATA, IDC])
        names = {name for name, _ in reference_containers(documents)}
        self.assertIn("reference-test-galaxy-job-1", names)


if __name__ == "__main__":
    unittest.main()
