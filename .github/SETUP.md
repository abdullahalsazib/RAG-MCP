# GitHub Actions Setup Guide

This guide explains how to set up the GitHub Actions workflow to automatically build and push Docker images to Docker Hub.

## Prerequisites

1. A GitHub repository (this project)
2. A Docker Hub account
3. Docker Hub access token (not your password)

## Step 1: Get Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/)
2. Sign in to your account
3. Click on your username → **Account Settings**
4. Go to **Security** → **New Access Token**
5. Give it a name (e.g., "GitHub Actions")
6. Set permissions to **Read, Write, Delete**
7. Copy the generated token (you won't see it again!)

## Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

### Required Secrets

- **Name**: `DOCKER_HUB_USERNAME`
  - **Value**: Your Docker Hub username

- **Name**: `DOCKER_HUB_ACCESS_TOKEN`
  - **Value**: The access token you created in Step 1 (NOT your password)

## Step 3: Image Naming

The workflow automatically creates images as:
- `{DOCKER_HUB_USERNAME}/mcp-server:latest` - On main/master branch pushes
- `{DOCKER_HUB_USERNAME}/mcp-server:{branch}-{sha}` - On other branch pushes  
- `{DOCKER_HUB_USERNAME}/mcp-server:{tag}` - On version tag pushes (e.g., v1.0.0)

If you want a custom image name, edit `.github/workflows/docker-publish.yml` and change the `IMAGE_NAME` variable.

## Step 4: Test the Workflow

The workflow will automatically trigger when:

1. **Push to main/master branch** - Creates tags like:
   - `latest`
   - `main-<sha>` (short commit hash)
   - `main` (branch name)

2. **Create a version tag** (e.g., `v1.0.0`) - Creates tags like:
   - `1.0.0`
   - `1.0`
   - `1`
   - `latest` (if it's the default branch)

3. **Manual trigger**:
   - Go to **Actions** tab
   - Select **Build and Push Docker Image**
   - Click **Run workflow**

4. **Pull Request** (builds only, doesn't push)

## Verifying the Build

1. Go to the **Actions** tab in your GitHub repository
2. You should see the workflow running
3. Once complete, check Docker Hub:
   ```
   https://hub.docker.com/r/YOUR_USERNAME/mcp-server
   ```

## Using the Image

After the workflow completes, you can pull and run the image:

```bash
docker pull YOUR_USERNAME/mcp-server:latest
docker run -d -p 8000:8000 YOUR_USERNAME/mcp-server:latest
```

## Troubleshooting

### Workflow fails with "authentication required"

- Check that `DOCKER_HUB_USERNAME` and `DOCKER_HUB_ACCESS_TOKEN` secrets are set correctly
- Verify the access token has the right permissions (Read, Write, Delete)

### Image name is wrong

- The image name format is: `{DOCKER_HUB_USERNAME}/mcp-server`
- Edit the workflow file to change the image name if needed

### Build fails

- Check the workflow logs in the Actions tab
- Ensure `Dockerfile` exists and is valid
- Verify `requirements.txt` is present

