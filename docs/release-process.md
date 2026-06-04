# Release Process

This document describes how the Galaxy Helm chart is versioned, released, and
published. The process is fully automated via GitHub Actions and gated by a
manual approval step, so a release happens only when a maintainer intends it to.

## Overview

```
dev (development)  ──PR──▶  master  ──merge triggers──▶  Release workflow
                                                              │
                          ┌───────────────────────────────────┤
                          ▼                ▼                    ▼
                  bump Chart.yaml   package & publish    tag + GitHub release
                          │          to CloudVE/helm-charts        │
                          ▼                                        ▼
                  merge master ──▶ dev          notify Slack + trigger
                                                galaxy-k8s-boot update
```

The chart `version` (the **Helm chart** version) is bumped **automatically** by
the release workflow — never edit it by hand on `dev`. The `appVersion` (the
**Galaxy application** version) *is* maintained by hand and should be updated
together with the Galaxy image `tag` in `galaxy/values.yaml` whenever Galaxy
itself is upgraded.

## Branch model

| Branch   | Purpose                                  | Protection |
|----------|------------------------------------------|------------|
| `dev`    | Integration branch; all work lands here  | Relaxed — status checks required, direct pushes allowed for maintainers |
| `master` | Release branch; every merge is a release | Strict — PR + approval + status checks, no direct pushes (except the release GitHub App) |

All release PRs **must** originate from `dev` and target `master`. This is
enforced by `.github/workflows/pr-validation.yaml`.

## How to cut a release

1. **Develop on `dev`.** Land all changes for the release into `dev` via normal
   PRs. Make sure `appVersion` in `galaxy/Chart.yaml` and the Galaxy image `tag`
   in `galaxy/values.yaml` reflect the Galaxy version you are shipping.

2. **Open a release PR `dev` → `master`.** The PR **must** carry exactly one
   version-bump label that determines the new chart version:

   | Label   | Effect on chart `version` | Example          |
   |---------|---------------------------|------------------|
   | `major` | `X.0.0`                   | `6.7.3 → 7.0.0`  |
   | `minor` | `x.Y.0`                   | `6.7.3 → 6.8.0`  |
   | `patch` | `x.y.Z`                   | `6.7.3 → 6.7.4`  |

   `pr-validation.yaml` fails the PR if the source branch is not `dev` or if the
   label count is not exactly one.

3. **Pass checks and get approval.** The `linting` and `test` status checks
   (from `test.yaml`) must pass. Approve the PR via a normal review, or comment
   `/approve` (maintainers with write access only — see `auto-approve.yaml`).
   On approval, auto-merge is enabled (`enable-auto-merge.yaml`).

4. **Merge to `master`.** Merging the PR triggers `release.yaml`, which:
   1. Re-runs the smoke test (`test.yaml`).
   2. Calculates the new chart `version` from the PR label.
   3. **Waits at the `release` environment approval gate** — a maintainer must
      approve the deployment in the GitHub UI for the release to proceed.
   4. Bumps `version:` in `galaxy/Chart.yaml`, commits, and pushes to `master`.
   5. Packages the chart and pushes the `.tgz` + updated `index.yaml` to
      [`CloudVE/helm-charts`](https://github.com/CloudVE/helm-charts).
   6. Creates a `v<version>` git tag and a GitHub release with generated notes.
   7. Merges `master` back into `dev` so the version bump is reflected there.
   8. Triggers a `repository_dispatch` to `galaxyproject/galaxy-k8s-boot` to
      update its pinned chart version, and posts a Slack notification.

### Manual / out-of-band releases

The release workflow can also be started by hand via
**Actions → Release → Run workflow** (`workflow_dispatch`), choosing the
`major`/`minor`/`patch` bump explicitly. The same approval gate applies.

## Versioning rules of thumb

- **Chart `version`** (`galaxy/Chart.yaml`) — bumped *only* by the release
  workflow. Do not edit it on `dev`; if you change it locally for testing,
  revert before committing.
- **`appVersion`** (`galaxy/Chart.yaml`) — the Galaxy release being shipped
  (e.g. `26.0.0`). Update by hand when upgrading Galaxy.
- **Galaxy image `tag`** (`galaxy/values.yaml`, `image.tag`) — must match the
  `appVersion`. Confirm the tag exists on
  [quay.io/galaxyproject/galaxy-min](https://quay.io/repository/galaxyproject/galaxy-min?tab=tags)
  before releasing.

## Configuration prerequisites

These are configured once per repository:

- **Branch protection rulesets** — see [`REPOSITORY_RULESETS_GUIDE.md`](./REPOSITORY_RULESETS_GUIDE.md).
  Status checks `linting` and `test` must match the job names in `test.yaml`.
- **`release` environment** — a GitHub Environment named `release` with required
  reviewers, providing the manual approval gate.
- **GitHub App secrets** — `HELM_UPDATER_APP_ID` and `HELM_UPDATER_PKEY` for a
  GitHub App that can bypass branch protection to push the version bump, tag,
  and downstream updates. The App needs access to `galaxy-helm`, `helm-charts`,
  and `galaxy-k8s-boot`.
- **`K8S_SLACK_WEBHOOK_URL`** — Slack incoming webhook for release notifications.

## Workflow reference

| Workflow                              | Trigger                              | Purpose |
|---------------------------------------|--------------------------------------|---------|
| `.github/workflows/test.yaml`         | push/PR to `master`/`dev`, called by release | Helm lint + full K3s deploy smoke test (verifies `appVersion` matches the running Galaxy API) |
| `.github/workflows/pr-validation.yaml`| PR to `master`                       | Enforces source branch `dev` and exactly one version label |
| `.github/workflows/auto-approve.yaml` | `/approve` PR comment                | Lets write-access maintainers approve + enable auto-merge |
| `.github/workflows/enable-auto-merge.yaml` | PR review approved             | Enables auto-merge once a PR to `master` is approved |
| `.github/workflows/release.yaml`      | PR to `master` merged, or manual     | Bump, package, publish, tag, merge-back, notify, downstream dispatch |

## Cross-repository integration

A successful release dispatches an `update-galaxy-chart` event to
`galaxyproject/galaxy-k8s-boot`, which updates its pinned `galaxy_chart_version`
and opens a PR there for review. See the galaxy-k8s-boot repository for that
side of the integration.
