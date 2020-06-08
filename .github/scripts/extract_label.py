#!/usr/bin/env python
import json
import os
import yaml

chartName = os.getenv('CHART_NAME')

with open(chartName + "/Chart.yaml", 'r') as chart:
    d = yaml.safe_load(chart)

bump = None
labels = [l.get("name")
          for l in json.loads(os.environ['GITHUB_CONTEXT'])['event']
          ['pull_request'].get('labels', [])]

if "patch" in labels:
    bump = "patch"
elif "feature" in labels:
    bump = "minor"
elif "version" in labels:
    bump = "major"

if bump:
    print(" ".join([d['version'], bump]))
else:
    print("nobump")
