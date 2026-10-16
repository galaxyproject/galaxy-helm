"""Verify that rendered initialization seeds genuine built-in keys safely."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from test_refdata import render


def registry_configuration(overrides=None):
    documents = render(overrides)
    config = next(d for d in documents if d["metadata"]["name"].endswith("-configs"))
    contents = config.get("data", config.get("stringData"))
    initialization = next(
        container
        for document in documents if document["kind"] == "Job"
        for container in document["spec"]["template"]["spec"]["containers"]
        if container["name"] == "galaxy-init-mounts"
    )
    return contents, initialization


class FeatureCountsRegistryTests(unittest.TestCase):
    def test_fresh_initialization_and_existing_registry(self):
        contents, initialization = registry_configuration()
        table = ElementTree.fromstring(contents["shed_tool_data_table_conf.xml"]).find(
            "./table[@name='featurecounts_anno']/file"
        )
        self.assertEqual(table.get("path"), "/galaxy/server/config/mutable/featurecounts_anno.loc")
        seed = next(
            command.strip() for command in initialization["args"][2].split(";")
            if command.strip().startswith("cp ") and "/featurecounts_anno.loc " in command
        )
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config"
            (config / "mutable").mkdir(parents=True)
            source = config / "featurecounts_anno.loc"
            target = config / "mutable/featurecounts_anno.loc"
            source.write_text(contents["featurecounts_anno.loc"])
            command = seed.replace("/galaxy/server/config", str(config))
            subprocess.run(["sh", "-c", command], check=True)
            rows = [line.split("\t") for line in target.read_text().splitlines() if line and not line.startswith("#")]
            self.assertEqual(rows, [[key, key] for key in ["hg38", "hg19", "mm10", "mm9"]])
            custom = "# Administrator-managed registry\nhg19\thg19\n"
            target.write_text(custom)
            # BSD cp -n returns 1 when it preserves an existing destination.
            subprocess.run(["sh", "-c", command], check=False)
            self.assertEqual(target.read_text(), custom)
        self.assertNotIn("gene_sets.loc", contents)

    def test_registry_is_mounted_without_reference_data_and_with_secret_configs(self):
        contents, initialization = registry_configuration({
            "refdata": {"enabled": False}, "useSecretConfigs": True,
        })
        self.assertIn("featurecounts_anno.loc", contents)
        self.assertIn("/galaxy/server/config/mutable/featurecounts_anno.loc", initialization["args"][2])
        self.assertTrue(any(
            mount["mountPath"] == "/galaxy/server/config/featurecounts_anno.loc"
            and mount["subPath"] == "featurecounts_anno.loc"
            for mount in initialization["volumeMounts"]
        ))

    def test_administrator_can_disable_or_override_seed(self):
        contents, initialization = registry_configuration({"configs": {"featurecounts_anno.loc": None}})
        self.assertNotIn("featurecounts_anno.loc", contents)
        self.assertNotIn("featurecounts_anno.loc", initialization["args"][2])
        custom = "hg19\thg19\n"
        contents, _ = registry_configuration({"configs": {"featurecounts_anno.loc": custom}})
        self.assertEqual(contents["featurecounts_anno.loc"], custom)


if __name__ == "__main__":
    unittest.main()
