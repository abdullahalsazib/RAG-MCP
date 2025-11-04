# Docker Setup Guide

This guide explains how to build and run the mcp-server using Docker.

## Prerequisites

- Docker installed on your system
- Docker Hub account (for pushing images)

## GitHub Secrets Setup

For automated builds, add these secrets to your GitHub repository:

- `DOCKER_HUB_USERNAME` - Your Docker Hub username
- `DOCKER_HUB_ACCESS_TOKEN` - Your Docker Hub access token (not password)

See `.github/SETUP.md` for detailed instructions.

## Building the Docker Image

### Build locally

```bash
docker build -t mcp-server:latest .
```

### Build with custom tag

```bash
docker build -t your-dockerhub-username/mcp-server:v1.0.0 .
```

## Running the Container

### Basic run

```bash
docker run -d \
  -p 8000:8000 \
  --name mcp-server \
  mcp-server:latest
```

### Run with environment variables

```bash
docker run -d \
  -p 8000:8000 \
  --name mcp-server \
  -e OPENAI_API_KEY=your-api-key \
  -e PORT=8000 \
  mcp-server:latest
```

### Run with Docker Compose

```bash
# Create a .env file with your configuration
echo "OPENAI_API_KEY=your-api-key" > .env

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Configuration

The container expects configuration files in the `config/` directory:
- `config/llm_config.json` - LLM provider configuration
- `config/mcp_servers.json` - MCP server endpoints

### Option 1: Mount config directory

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config:ro \
  mcp-server:latest
```

### Option 2: Copy config into image (for custom builds)

Modify the Dockerfile to include your config:

```dockerfile
COPY config/ ./config/
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port (default: 8000) | No |
| `OPENAI_API_KEY` | OpenAI API key | Yes (if using OpenAI) |
| `MCP_SERVERS` | JSON array of MCP servers | No |
| `BASE_URL` | Base URL for the application | No |
| `RENDER_EXTERNAL_URL` | External URL (for Render.com) | No |

## Health Check

The container includes a health check endpoint:

```bash
curl http://localhost:8000/health
```

## Pushing to Docker Hub

### Manual Push

```bash
# Tag the image
docker tag mcp-server:latest your-dockerhub-username/mcp-server:latest

# Login to Docker Hub
docker login

# Push the image
docker push your-dockerhub-username/mcp-server:latest
```

### Automated Push with GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/docker-publish.yml`) that automatically builds and pushes the Docker image when you:

1. Push to `main` or `master` branch
2. Create a version tag (e.g., `v1.0.0`)
3. Manually trigger the workflow

#### Setup GitHub Secrets

Go to your repository Settings → Secrets and variables → Actions, and add:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token (not password)

#### Using the Image

After the workflow completes, you can pull and run:

```bash
docker pull your-dockerhub-username/mcp-server:latest
docker run -d -p 8000:8000 your-dockerhub-username/mcp-server:latest
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs mcp-server
```

### Port already in use

Use a different port:
```bash
docker run -d -p 8080:8000 mcp-server:latest
```

### Configuration not found

Ensure config files exist:
```bash
ls -la config/
```

### Health check failing

Check if the application is running:
```bash
docker exec -it mcp-server curl http://localhost:8000/health
```

## Multi-Architecture Builds

The GitHub Actions workflow builds for both `linux/amd64` and `linux/arm64`. For local multi-arch builds:

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t your-dockerhub-username/mcp-server:latest --push .
```

