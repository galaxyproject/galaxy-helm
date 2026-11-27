"""Check the marker files that make Galaxy pods wait for the setup jobs.

The init-db and init-mounts jobs write marker files to the shared volume when they finish, and
every Galaxy pod has an init container that waits for them. The marker names must differ between
rollouts, or pods would find an earlier rollout's marker and start before this rollout's database
migration and file copy have finished.

Run with: python -m unittest discover -s tests -v (requires Helm and PyYAML).
"""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

CHART = Path(__file__).resolve().parents[1] / "galaxy"
MUTABLE = "/galaxy/server/config/mutable"
WRITE = re.compile(rf"> {MUTABLE}/(init_[a-z]+_done)_(\w+)")
WAIT = re.compile(rf"until \[ -f {MUTABLE}/(init_[a-z]+_done)_(\w+) \]")
GALAXY_DEPLOYMENTS = {
    "marker-test-galaxy-web", "marker-test-galaxy-job-0", "marker-test-galaxy-workflow",
    "marker-test-galaxy-celery", "marker-test-galaxy-celery-beat",
}
# Without a password the chart generates a random one, so the Galaxy configuration (and the
# checksums of it in every pod) differs on each render. Argo CD deployments must set it.
FIXED_PASSWORD = {"postgresql": {"galaxyDatabasePassword": "not-random"}}


def render(overrides=None):
    with tempfile.TemporaryDirectory() as directory:
        values = Path(directory) / "values.yaml"
        values.write_text(yaml.safe_dump(overrides or {}))
        output = subprocess.check_output(
            ["helm", "template", "marker-test", str(CHART), "-n", "galaxy", "-f", str(values)],
            text=True,
        )
    return [document for document in yaml.safe_load_all(output) if document]


def scripts(document):
    pod = document["spec"]["template"]["spec"]
    for container in pod.get("initContainers", []) + pod.get("containers", []):
        yield " ".join(container.get("command", []) + container.get("args", []))


def written_markers(documents):
    return {
        marker
        for document in documents if document["kind"] == "Job"
        for script in scripts(document)
        for marker in WRITE.findall(script)
    }


def waited_markers(documents):
    waits = {}
    for document in documents:
        if document["kind"] != "Deployment":
            continue
        markers = {marker for script in scripts(document) for marker in WAIT.findall(script)}
        if markers:
            waits[document["metadata"]["name"]] = markers
    return waits


def marker_suffixes(documents):
    suffixes = {}
    for name, suffix in written_markers(documents):
        suffixes.setdefault(name, set()).add(suffix)
    return suffixes


class SetupMarkerTests(unittest.TestCase):
    def test_every_galaxy_pod_waits_for_exactly_the_markers_the_setup_jobs_write(self):
        documents = render({
            "jobHandlers": {"replicaCount": 2},
            "setupJob": {"downloadToolConfs": {"enabled": True}},
        })
        written = written_markers(documents)
        self.assertEqual({name for name, _ in written}, {"init_db_done", "init_mounts_done", "init_clone_done"})
        waits = waited_markers(documents)
        self.assertEqual(set(waits), GALAXY_DEPLOYMENTS | {"marker-test-galaxy-job-1"})
        for deployment, markers in waits.items():
            with self.subTest(deployment=deployment):
                self.assertEqual(markers, written)

    def test_markers_are_identical_when_the_same_values_are_rendered_again(self):
        # Argo CD compares the live objects with a fresh `helm template` on every refresh, and the
        # marker names are part of every Galaxy pod spec.
        self.assertEqual(written_markers(render(FIXED_PASSWORD)), written_markers(render(FIXED_PASSWORD)))

    def test_markers_change_when_an_input_of_the_setup_jobs_changes(self):
        # `helm template` always renders revision 1, so under Argo CD the content of the setup
        # jobs is all that can tell this rollout's markers apart from an earlier rollout's.
        before = marker_suffixes(render(FIXED_PASSWORD))
        self.assertEqual(set(before), {"init_db_done", "init_mounts_done", "init_clone_done"})
        changes = {
            "image": {"image": {"tag": "a-newer-release"}},
            "galaxy config": {"configs": {"galaxy.yml": {"galaxy": {"brand": "Renamed"}}}},
            "setup job": {"setupJob": {"createDatabase": False}},
        }
        for change, override in changes.items():
            with self.subTest(change=change):
                after = marker_suffixes(render({**FIXED_PASSWORD, **override}))
                self.assertEqual(set(after), set(before))
                for name in before:
                    self.assertEqual(len(after[name]), 1)
                    self.assertTrue(after[name].isdisjoint(before[name]), name)

    def test_markers_unchanged_by_values_the_setup_jobs_do_not_use(self):
        # A new marker name restarts every Galaxy pod, so values that only affect other
        # resources must not change it.
        before = written_markers(render(FIXED_PASSWORD))
        changes = {
            "web replicas": {"webHandlers": {"replicaCount": 3}},
            "tusd replicas": {"tusd": {"replicaCount": 2}},
            "nginx image": {"nginx": {"image": {"tag": "another-release"}}},
        }
        for change, override in changes.items():
            with self.subTest(change=change):
                self.assertEqual(written_markers(render({**FIXED_PASSWORD, **override})), before)


if __name__ == "__main__":
    unittest.main()
