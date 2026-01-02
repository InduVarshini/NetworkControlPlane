# Setting Up GitHub Repository

Follow these steps to initialize git and connect to GitHub.

## Step 1: Initialize Git Repository

```bash
cd /Users/indu/cursor-projects/NetworkControlPlane

# Initialize git repository
git init

# Verify it's initialized
git status
```

## Step 2: Add All Files

```bash
# Add all files to staging
git add .

# Check what will be committed
git status
```

You should see all your project files staged for commit. The `.gitignore` will automatically exclude:
- `__pycache__/` directories
- `*.pyc` files
- Other temporary files

## Step 3: Make Initial Commit

```bash
git commit -m "Initial commit: NetworkControlPlane with file upload feature

- YAML file upload via web UI
- Network topology deployment
- Telemetry collection
- Network validation
- Docker support"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `NetworkControlPlane` (or your preferred name)
3. Description: "Centralized Network Configuration, Automation, and Observability"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 5: Connect and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/NetworkControlPlane.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 6: Verify

1. Go to your GitHub repository page
2. Verify all files are there
3. Check that README.md displays correctly

## Optional: Set Up GitHub Actions for Docker

After pushing, set up automated Docker builds:

1. Go to: **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Add these secrets:
   - **Name**: `DOCKERHUB_USERNAME`
     - **Value**: Your Docker Hub username
   - **Name**: `DOCKERHUB_TOKEN`
     - **Value**: Your Docker Hub access token
       - Get token from: Docker Hub → Account Settings → Security → New Access Token

4. Push any change to trigger the workflow, or manually run it from Actions tab

## Troubleshooting

### "fatal: remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/YOUR_USERNAME/NetworkControlPlane.git
```

### "Permission denied (publickey)"
If you use SSH instead of HTTPS:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/NetworkControlPlane.git
```

### Files not showing up
Make sure `.gitignore` isn't excluding important files:
```bash
# Check what's ignored
git status --ignored
```

## Next Steps

After pushing to GitHub:

1. **Update README.md** - Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username
2. **Push Docker Image** - Run `./push-to-dockerhub.sh YOUR_USERNAME`
3. **Add Badges** (optional) - Add to README.md:
   ```markdown
   ![Docker](https://img.shields.io/docker/pulls/YOUR_USERNAME/network-control-plane)
   ![GitHub](https://img.shields.io/github/license/YOUR_USERNAME/NetworkControlPlane)
   ```

## Quick Command Summary

```bash
cd /Users/indu/cursor-projects/NetworkControlPlane
git init
git add .
git commit -m "Initial commit: NetworkControlPlane"
git remote add origin https://github.com/YOUR_USERNAME/NetworkControlPlane.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username!

