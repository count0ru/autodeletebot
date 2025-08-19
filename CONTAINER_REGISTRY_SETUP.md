# 🐳 GitHub Container Registry Setup Guide

This guide will help you fix the container registry permission issues in your CI/CD pipeline.

## ❌ **Current Issue**

Your deployment workflow is failing with this error:
```
ERROR: failed to build: failed to solve: failed to push ghcr.io/count0ru/autodeletebot:main: denied: installation not allowed to Create organization package
```

## 🔧 **Solution 1: Enable Actions Permissions (Recommended)**

### **Step 1: Go to Repository Settings**
1. Navigate to [https://github.com/count0ru/autodeletebot](https://github.com/count0ru/autodeletebot)
2. Click **Settings** tab
3. Click **Actions** in the left sidebar
4. Click **General**

### **Step 2: Configure Permissions**
1. Scroll down to **Workflow permissions**
2. Select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

### **Step 3: Verify Changes**
- The workflow will now have permission to push to `ghcr.io/count0ru/autodeletebot`
- Docker images will be automatically pushed on each deployment

## 🔑 **Solution 2: Personal Access Token (Alternative)**

If Solution 1 doesn't work, you can use a Personal Access Token:

### **Step 1: Create Personal Access Token**
1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a name like "AutoDeleteBot CI/CD"
4. Select scopes:
   - `repo` (full control of private repositories)
   - `write:packages` (upload packages to GitHub Package Registry)
   - `delete:packages` (delete packages from GitHub Package Registry)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)

### **Step 2: Add Token to Repository Secrets**
1. Go back to your repository: [https://github.com/count0ru/autodeletebot](https://github.com/count0ru/autodeletebot)
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `CR_PAT`
5. Value: Paste your personal access token
6. Click **Add secret**

### **Step 3: Update Workflow**
Update `.github/workflows/deploy.yml` to use the token:

```yaml
- name: Login to Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.CR_PAT }}
```

## 🚀 **Solution 3: Use Docker Hub Instead**

If you prefer to use Docker Hub instead of GitHub Container Registry:

### **Step 1: Create Docker Hub Account**
1. Go to [https://hub.docker.com](https://hub.docker.com)
2. Create an account if you don't have one
3. Create a repository named `autodeletebot`

### **Step 2: Add Docker Hub Secrets**
1. Go to your GitHub repository settings
2. Add these secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

### **Step 3: Update Workflow**
Update `.github/workflows/deploy.yml`:

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ secrets.DOCKERHUB_USERNAME }}/autodeletebot:latest,${{ secrets.DOCKERHUB_USERNAME }}/autodeletebot:${{ github.sha }}
```

## 🔍 **Current Workflow Status**

Your current workflow:
- ✅ **Builds Docker images locally**
- ✅ **Runs deployment simulation**
- ❌ **Cannot push to container registry** (permission issue)

## 📋 **Quick Fix Commands**

```bash
# Option 1: Fix permissions (recommended)
# Go to Settings → Actions → General → Read and write permissions

# Option 2: Use Docker Hub
# Create Docker Hub account and add secrets

# Option 3: Continue with local builds only
# Current workflow works for testing and development
```

## 🎯 **Recommended Approach**

1. **Start with Solution 1** (enable Actions permissions)
2. **Test the workflow** - it should now push images successfully
3. **If it still fails**, use Solution 2 (Personal Access Token)
4. **For production**, consider Solution 3 (Docker Hub) for better reliability

## 📊 **Expected Results**

After fixing permissions:
- ✅ Docker images will be pushed to `ghcr.io/count0ru/autodeletebot`
- ✅ Deployment workflow will complete successfully
- ✅ Images will be available for pulling and deployment
- ✅ Full CI/CD pipeline will work end-to-end

## 🆘 **Need Help?**

If you're still having issues:
1. Check the GitHub Actions logs for specific error messages
2. Verify your repository permissions
3. Ensure you have admin access to the repository
4. Check if your organization has any restrictions on Actions

---

**🎉 Once fixed, your Auto-Delete Bot will have a complete CI/CD pipeline with automated Docker image building and deployment!**
