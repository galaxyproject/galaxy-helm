# Repository Rulesets Configuration Guide

This directory contains JSON ruleset configurations for setting up branch protection rules via GitHub's Repository Rulesets feature.

## 📁 Files Overview

### Combined Rulesets (Recommended for simplicity)
- `galaxy-helm-ruleset.json` - Single ruleset covering both master and dev branches
- `galaxy-k8s-boot-ruleset.json` - Single ruleset for galaxy-k8s-boot repository

### Branch-Specific Rulesets (Recommended for granular control)
- `galaxy-helm-master-ruleset.json` - Strict rules for master branch
- `galaxy-helm-dev-ruleset.json` - Relaxed rules for dev branch
- `galaxy-k8s-boot-master-ruleset.json` - Strict rules for master branch  
- `galaxy-k8s-boot-dev-ruleset.json` - Relaxed rules for dev branch

## 🚀 Quick Setup

### Option 1: GitHub Web UI
1. Go to **Settings → Rules → Rulesets**
2. Click **New ruleset**
3. Copy and paste the JSON content from the appropriate file
4. Update the `actor_id` values for your GitHub App and team members
5. Click **Create ruleset**

### Option 2: GitHub CLI
```bash
# Create ruleset from JSON file
gh api repos/:owner/:repo/rulesets \
  --method POST \
  --input galaxy-helm-master-ruleset.json

# List existing rulesets
gh api repos/:owner/:repo/rulesets
```

### Option 3: GitHub API
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets \
  -d @galaxy-helm-master-ruleset.json
```

## 🔧 Required Customizations

Before applying these rulesets, you **MUST** update the following:

### 1. GitHub App Integration ID
Replace `"actor_id": null` with your actual GitHub App's integration ID:

```json
{
  "actor_id": 12345678,
  "actor_type": "Integration", 
  "bypass_mode": "always"
}
```

**To find your GitHub App ID:**
```bash
# Using GitHub CLI
gh api /app

# Using curl
curl -H "Authorization: Bearer YOUR_APP_TOKEN" \
     https://api.github.com/app
```

### 2. Repository Role IDs (Optional)
Update repository role actor IDs if you want specific teams to have bypass permissions:

```json
{
  "actor_id": 87654321,
  "actor_type": "RepositoryRole",
  "bypass_mode": "pull_request"
}
```

## 📋 Ruleset Differences

### Master Branch Rules
- ✅ **Strict PR requirements:** Required approvals, stale review dismissal
- ✅ **Required status checks:** linting, test
- ✅ **Linear history required** (no merge commits)
- ✅ **Signed commits required** 
- ✅ **No direct pushes** except via GitHub App
- ✅ **Branch deletion protection**

### Dev Branch Rules  
- ✅ **Basic PR requirements:** 1 approval required
- ✅ **Required status checks:** linting, test
- ❌ **No stale review dismissal** (more flexible)
- ❌ **No code owner requirement** (faster development)
- ❌ **No linear history requirement** (allows merge commits)
- ❌ **No signed commit requirement**
- ✅ **Allow direct pushes by maintainers** (for hotfixes)

## 🔍 Status Check Configuration

The rulesets expect these status checks to be available:
- `linting` (from test.yaml workflow)
- `test` (from test.yaml workflow)

**Important:** Status check names must exactly match your workflow job names.

## 🛠 Troubleshooting

### Common Issues

**1. Status checks not found:**
- Verify workflow job names match status check contexts
- Ensure workflows have run at least once on the branch

**2. GitHub App can't bypass rules:**
- Check that the App ID is correct in the ruleset
- Verify the App has necessary permissions (Contents: Write, Pull Requests: Write)
- Ensure the App is installed on the repository

**3. Ruleset not applying:**
- Check that branch names match the `ref_name.include` patterns
- Verify enforcement is set to "active" not "evaluate"
- Confirm no conflicting legacy branch protection rules exist

### Testing Rulesets

1. **Create a test branch:**
   ```bash
   git checkout -b test-ruleset
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: verify rulesets work"
   git push origin test-ruleset
   ```

2. **Create a test PR:**
   - Open PR from test-ruleset → master
   - Verify status checks are required
   - Test that direct pushes to master are blocked

3. **Test GitHub App bypass:**
   - Manually trigger a release workflow
   - Verify the App can push to protected branches

## 📚 Additional Resources

- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [GitHub API Rulesets Reference](https://docs.github.com/en/rest/repos/rulesets)
- [GitHub Apps Permissions](https://docs.github.com/en/developers/apps/building-github-apps/setting-permissions-for-github-apps)

## 🔄 Updates

When updating rulesets:
1. Test changes in a fork or test repository first
2. Use "evaluate" mode to preview rule effects
3. Monitor for broken workflows after applying changes
4. Keep ruleset JSON files in version control for auditability