# Publishing to Docker Hub

This guide explains how to publish the NetworkControlPlane Docker image to Docker Hub.

## Prerequisites

1. **Docker Hub Account**: Sign up at https://hub.docker.com (free)
2. **Docker Installed**: Make sure Docker is installed and running
3. **Logged In**: Login to Docker Hub: `docker login`

## Method 1: Using the Script (Easiest)

```bash
# Make script executable (if not already)
chmod +x push-to-dockerhub.sh

# Run the script
./push-to-dockerhub.sh YOUR_DOCKERHUB_USERNAME

# Or specify a tag
./push-to-dockerhub.sh YOUR_DOCKERHUB_USERNAME v1.0.0
```

The script will:
1. Build the Docker image
2. Tag it with your Docker Hub username
3. Push it to Docker Hub

## Method 2: Manual Steps

### Step 1: Build the Image

```bash
docker build -t YOUR_DOCKERHUB_USERNAME/network-control-plane:latest .
```

### Step 2: Tag the Image (Optional)

If you want to tag a specific version:

```bash
docker tag YOUR_DOCKERHUB_USERNAME/network-control-plane:latest \
           YOUR_DOCKERHUB_USERNAME/network-control-plane:v1.0.0
```

### Step 3: Push to Docker Hub

```bash
# Push latest tag
docker push YOUR_DOCKERHUB_USERNAME/network-control-plane:latest

# Push version tag (if created)
docker push YOUR_DOCKERHUB_USERNAME/network-control-plane:v1.0.0
```

## Method 3: Automated with GitHub Actions

### Setup

1. **Add Docker Hub Secrets** to your GitHub repository:
   - Go to: Settings → Secrets and variables → Actions
   - Add secret: `DOCKERHUB_USERNAME` (your Docker Hub username)
   - Add secret: `DOCKERHUB_TOKEN` (your Docker Hub access token)

2. **Create Docker Hub Access Token**:
   - Go to Docker Hub → Account Settings → Security
   - Click "New Access Token"
   - Copy the token and add it as `DOCKERHUB_TOKEN` secret

3. **Push to GitHub**:
   - The workflow will automatically build and push on:
     - Push to `main`/`master` branch
     - Creating a version tag (e.g., `v1.0.0`)
     - Manual workflow dispatch

### Using the Workflow

The workflow will automatically:
- Build the Docker image
- Push to Docker Hub with appropriate tags
- Cache layers for faster builds

## Verifying the Push

After pushing, verify your image is on Docker Hub:

```bash
# Pull and test
docker pull YOUR_DOCKERHUB_USERNAME/network-control-plane:latest

# Run it
docker run -it --rm --privileged \
  -p 5001:5001 \
  YOUR_DOCKERHUB_USERNAME/network-control-plane:latest \
  python3 -m network_control_plane.ui
```

Visit https://hub.docker.com/r/YOUR_DOCKERHUB_USERNAME/network-control-plane to see your published image.

## Image Tags

Recommended tagging strategy:

- `latest` - Always points to the most recent stable version
- `v1.0.0` - Specific version tags (semantic versioning)
- `main` - Builds from main branch (via GitHub Actions)

## Example: Complete Workflow

```bash
# 1. Login to Docker Hub
docker login

# 2. Build and push using script
./push-to-dockerhub.sh myusername latest

# 3. Test the published image
docker pull myusername/network-control-plane:latest
docker run -it --rm --privileged \
  -p 5001:5001 \
  -v $(pwd):/workspace \
  -w /workspace \
  myusername/network-control-plane:latest \
  python3 -m network_control_plane.ui
```

## Troubleshooting

### "denied: requested access to the resource is denied"
- Make sure you're logged in: `docker login`
- Verify your Docker Hub username is correct
- Check that the repository name matches your username

### "unauthorized: authentication required"
- Your Docker Hub token may have expired
- Generate a new access token and update GitHub secrets

### Build fails
- Check Docker is running: `docker info`
- Verify Dockerfile is correct
- Check build logs for specific errors

