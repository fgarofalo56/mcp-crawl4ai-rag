# 🐳 WSL2 Docker Integration Fix

Fix for "docker command not found" error in WSL2 environments.

## Table of Contents

- [Problem Description](#problem-description)
- [Root Cause](#root-cause)
- [Solution](#solution)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Alternative Solutions](#alternative-solutions)

---

## Problem Description

**Symptom**: When running Docker commands in WSL2, you get the following error:

```bash
The command 'docker' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.

For details about using Docker Desktop with WSL 2, visit:
https://docs.docker.com/go/wsl2/
```

**Impact**:
- Cannot run `docker` or `docker-compose` commands
- Cannot start the MCP server with `docker-compose up`
- Cannot manage Docker containers from WSL2

**Environment**:
- Windows 10/11 with WSL2
- Docker Desktop installed on Windows
- WSL2 distribution (Ubuntu, Debian, etc.)

---

## Root Cause

Docker Desktop for Windows includes a WSL2 backend, but the integration with specific WSL2 distributions must be explicitly enabled. By default, Docker Desktop may not be integrated with all your WSL2 distros.

When Docker Desktop isn't integrated:
- Docker daemon runs on Windows, but CLI isn't available in WSL2
- Docker commands work in PowerShell/CMD but not in WSL2 bash
- MCP server development requires Docker in WSL2 for proper workflow

---

## Solution

### Step 1: Verify Docker Desktop is Running

1. **Check Docker Desktop is installed**:
   - Open Windows Start menu
   - Search for "Docker Desktop"
   - If not installed, download from: https://www.docker.com/products/docker-desktop/

2. **Start Docker Desktop**:
   - Launch Docker Desktop from Windows
   - Wait for it to fully start (whale icon in system tray turns white)
   - You should see "Docker Desktop is running"

### Step 2: Enable WSL2 Integration

1. **Open Docker Desktop Settings**:
   - Click the Docker whale icon in Windows system tray
   - Click "Settings" (gear icon)

2. **Navigate to WSL Integration**:
   - In the left sidebar, click "Resources"
   - Click "WSL Integration"

3. **Enable WSL2 Backend** (if not already enabled):
   - Ensure "Use the WSL 2 based engine" is checked
   - If not, check it and click "Apply & Restart"

4. **Enable Your WSL2 Distribution**:
   - Under "Enable integration with additional distros:"
   - Find your WSL2 distribution (e.g., Ubuntu, Ubuntu-22.04, Debian)
   - Toggle the switch to **ON** (blue)
   - Click "Apply & Restart"

   **Screenshot reference**:
   ```
   ┌─────────────────────────────────────────┐
   │ Resources > WSL Integration             │
   ├─────────────────────────────────────────┤
   │ ☑ Use the WSL 2 based engine           │
   │                                         │
   │ Enable integration with additional      │
   │ distros:                                │
   │                                         │
   │ Ubuntu-22.04           [ON] ◀──────────│
   │ Debian                 [OFF]            │
   │ Ubuntu-20.04           [OFF]            │
   │                                         │
   │           [Apply & Restart]             │
   └─────────────────────────────────────────┘
   ```

5. **Wait for Docker Desktop to Restart**:
   - Docker Desktop will restart (takes 30-60 seconds)
   - System tray icon will show restart progress

### Step 3: Verify in WSL2

1. **Open your WSL2 terminal** (or restart current terminal)

2. **Test Docker command**:
   ```bash
   docker --version
   ```

   **Expected output**:
   ```
   Docker version 24.0.x, build xxxxx
   ```

3. **Test Docker Compose**:
   ```bash
   docker compose version
   ```

   **Expected output**:
   ```
   Docker Compose version v2.23.x
   ```

4. **Test Docker daemon connection**:
   ```bash
   docker ps
   ```

   **Expected output** (empty list is OK):
   ```
   CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
   ```

---

## Verification

### Quick Verification Checklist

Run these commands in your WSL2 terminal:

```bash
# 1. Check Docker CLI is available
docker --version                    # Should show version

# 2. Check Docker Compose (V2 syntax)
docker compose version              # Should show version

# 3. Check daemon connection
docker ps                          # Should list containers (or empty)

# 4. Test Docker functionality
docker run --rm hello-world        # Should download and run test container

# 5. Navigate to project and test
cd /mnt/e/Repos/GitHub/mcp-crawl4ai-rag
docker compose ps                  # Should show services (even if stopped)
```

### Expected Results

✅ **Success**: All commands execute without "command not found" errors

❌ **Still failing**: See [Troubleshooting](#troubleshooting) section

### Test MCP Docker Setup

Once Docker is working, test the MCP setup:

```bash
cd /mnt/e/Repos/GitHub/mcp-crawl4ai-rag

# Check configuration
cat docker-compose.yml    # Should display compose file

# Pull images (don't start yet)
docker compose pull

# Check services defined
docker compose config

# Start services (if environment is configured)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs
```

---

## Troubleshooting

### Issue 1: "Apply & Restart" Button Greyed Out

**Cause**: Docker Desktop requires administrative privileges or is in the middle of an operation.

**Solutions**:
1. Close and restart Docker Desktop as Administrator
2. Wait for any pending operations to complete
3. Restart Windows if persistent

### Issue 2: WSL2 Distribution Not Listed

**Cause**: Your WSL2 distro isn't detected by Docker Desktop.

**Solutions**:

1. **Verify WSL2 distribution exists**:
   ```powershell
   # Run in PowerShell (not WSL2)
   wsl --list --verbose
   ```

   Expected output showing VERSION 2:
   ```
   NAME            STATE           VERSION
   * Ubuntu-22.04  Running         2
     Debian        Stopped         2
   ```

2. **Convert WSL1 to WSL2** (if VERSION shows 1):
   ```powershell
   # In PowerShell
   wsl --set-version Ubuntu-22.04 2
   ```

3. **Restart Docker Desktop** after conversion

### Issue 3: Docker Commands Still Not Found After Enabling

**Cause**: WSL2 terminal needs to reload environment.

**Solutions**:

1. **Restart WSL2 terminal**:
   - Close all WSL2 terminal windows
   - Open a new WSL2 terminal

2. **Restart WSL2 instance** (in PowerShell):
   ```powershell
   wsl --shutdown
   wsl
   ```

3. **Verify Docker integration paths**:
   ```bash
   # In WSL2
   echo $PATH | grep -o docker
   ls -la /usr/bin/docker
   ```

   Should show Docker in PATH and symlink at `/usr/bin/docker`

### Issue 4: Permission Denied Errors

**Cause**: User not in docker group (though this is usually automatic with Docker Desktop).

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or use:
newgrp docker

# Test
docker ps
```

### Issue 5: "Cannot connect to Docker daemon"

**Cause**: Docker Desktop not running or not integrated properly.

**Solutions**:

1. **Verify Docker Desktop is running**:
   - Check system tray for Docker whale icon
   - Icon should be white/colored (not gray)

2. **Restart Docker Desktop**:
   - Right-click Docker icon > Quit Docker Desktop
   - Start Docker Desktop again
   - Wait for "Docker Desktop is running"

3. **Check Docker service**:
   ```bash
   # In WSL2
   docker context ls
   ```

   Should show `default` context pointing to Docker Desktop

4. **Reinstall WSL2 integration**:
   - In Docker Desktop: Settings > Resources > WSL Integration
   - Toggle your distro OFF, Apply
   - Toggle your distro ON, Apply & Restart

### Issue 6: Docker Desktop Won't Start

**Cause**: Various Windows/Hyper-V issues.

**Solutions**:

1. **Restart Windows** (solves most issues)

2. **Check Hyper-V is enabled**:
   ```powershell
   # In PowerShell as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   ```

3. **Check WSL2 is enabled**:
   ```powershell
   # In PowerShell as Administrator
   wsl --update
   wsl --set-default-version 2
   ```

4. **Reinstall Docker Desktop**:
   - Uninstall Docker Desktop
   - Restart Windows
   - Download latest Docker Desktop
   - Install and enable WSL2 backend during setup

---

## Alternative Solutions

### Option 1: Install Docker Directly in WSL2 (Not Recommended)

⚠️ **Note**: This is more complex and loses Docker Desktop benefits (GUI, resource management, easy updates).

Only use if Docker Desktop doesn't work for your environment.

```bash
# In WSL2
# Remove any old Docker packages
sudo apt-get remove docker docker-engine docker.io containerd runc

# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test
docker run hello-world
```

**Downsides**:
- Must manually start Docker service each time: `sudo service docker start`
- No GUI management
- Doesn't share images/containers with Windows Docker Desktop
- More maintenance overhead

### Option 2: Use PowerShell for Docker Commands

Temporarily use PowerShell while fixing WSL2 integration:

```powershell
# In PowerShell (Windows)
cd E:\Repos\GitHub\mcp-crawl4ai-rag
docker compose up
```

**Downside**: Can't use bash scripts, less convenient for development.

---

## Prevention

To avoid this issue in the future:

1. **Always enable WSL integration** when installing Docker Desktop
2. **Keep Docker Desktop running** during development
3. **Update regularly**: Docker Desktop > Check for updates
4. **Bookmark** Docker Desktop WSL2 integration settings for quick access

---

## Related Documentation

- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/wsl/)
- [WSL2 Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Docker Compose with WSL2](https://docs.docker.com/compose/install/)
- [MCP Docker Setup Guide](../DOCKER_SETUP.md)
- [Main Troubleshooting Guide](../guides/TROUBLESHOOTING.md)

---

## Quick Reference

### Common Commands After Fix

```bash
# Start MCP server with Docker
cd /mnt/e/Repos/GitHub/mcp-crawl4ai-rag
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after changes
docker compose up --build

# Test single container
docker run --rm hello-world
```

---

**Last Updated**: October 28, 2025
**Issue**: Docker not available in WSL2
**Solution**: Enable Docker Desktop WSL2 integration
**Status**: ✅ Verified Solution
