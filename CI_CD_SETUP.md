# 🚀 CI/CD Pipeline Setup Guide

This guide explains how to set up and use the comprehensive CI/CD pipeline for your [Auto-Delete Telegram Bot](https://github.com/count0ru/autodeletebot).

## 📋 **What's Included**

### **1. GitHub Actions Workflows**
- **`ci-cd.yml`** - Main CI/CD pipeline (quality, testing, Docker, security)
- **`pr-check.yml`** - Quick PR validation with automated comments
- **`deploy.yml`** - Automated deployment to staging/production
- **`dependabot.yml`** - Automated dependency updates

### **2. Automated Processes**
- ✅ **Code Quality**: Pylint, flake8, black formatting
- 🧪 **Testing**: 34 test cases with pytest and coverage
- 🐳 **Docker**: Automated builds and registry pushes
- 🔒 **Security**: Bandit and Safety vulnerability scanning
- 🚀 **Deployment**: Multi-environment deployment automation
- 📦 **Dependencies**: Weekly security updates via Dependabot

## 🛠️ **Setup Instructions**

### **Step 1: Enable GitHub Actions**

1. Go to your repository: [https://github.com/count0ru/autodeletebot](https://github.com/count0ru/autodeletebot)
2. Click **Actions** tab
3. Click **Enable Actions** if not already enabled

### **Step 2: Configure Repository Secrets**

Go to **Settings** → **Secrets and variables** → **Actions** and add:

```bash
# For Docker Hub (optional)
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=your_dockerhub_access_token

# For deployment (if using external services)
DEPLOYMENT_TOKEN=your_deployment_token
```

### **Step 3: Enable Dependabot**

1. Go to **Security** → **Dependabot**
2. Click **Enable Dependabot**
3. The `.github/dependabot.yml` file will automatically configure:
   - Weekly Python dependency updates
   - Weekly GitHub Actions updates
   - Monthly Docker base image updates

## 🔄 **How It Works**

### **On Every Push/PR:**
1. **Quality Check** (`ci-cd.yml`)
   - Install dependencies
   - Run pylint (target: 10.00/10)
   - Run flake8 style checks
   - Run black formatting check
   - Execute 34 test cases
   - Generate coverage report

2. **Docker Build** (`ci-cd.yml`)
   - Build Docker image
   - Test image functionality
   - Cache layers for faster builds

3. **Security Scan** (`ci-cd.yml`)
   - Bandit security analysis
   - Safety dependency check

### **On Pull Requests:**
1. **Quick Check** (`pr-check.yml`)
   - Fast quality validation
   - Automated PR comments
   - Test execution
   - Format verification

### **On Releases:**
1. **Deploy** (`deploy.yml`)
   - Build production Docker image
   - Push to container registry
   - Deploy to production
   - Create GitHub release

### **Weekly (Dependabot):**
1. **Dependency Updates**
   - Check for security vulnerabilities
   - Create PRs for updates
   - Auto-approve safe updates
   - Run tests on updated dependencies

## 📊 **Pipeline Status**

### **Quality Gates**
- **Pylint Score**: Must be ≥ 9.0 (currently 10.00/10)
- **Test Coverage**: All 34 tests must pass
- **Code Format**: Black formatting check must pass
- **Security**: No high/critical vulnerabilities

### **Build Status**
- **Docker Build**: Must complete successfully
- **Image Test**: Must pass basic functionality test
- **Registry Push**: Must upload to container registry

## 🚀 **Deployment Environments**

### **Staging (main branch)**
- Automatic deployment on push to main
- Uses latest Docker image
- Environment: `staging`

### **Production (tags)**
- Automatic deployment on version tags (v1.0.0, v2.1.3, etc.)
- Uses tagged Docker image
- Environment: `production`

### **Manual Deployment**
```bash
# Go to Actions → Deploy → Run workflow
# Select environment: staging or production
```

## 📈 **Monitoring & Notifications**

### **Status Checks**
- All workflows show status in PRs
- Branch protection can require passing checks
- Deployment status visible in repository

### **Automated Comments**
- PR quality results
- Test execution status
- Dependabot update approvals

### **Artifacts**
- Test coverage reports
- Security scan results
- Build logs and status reports

## 🔧 **Customization**

### **Modify Quality Thresholds**
Edit `.pylintrc`:
```ini
[MASTER]
fail-under=9.0  # Minimum pylint score
```

### **Add New Tests**
1. Add test files to `tests/` directory
2. Update `requirements-test.txt` if needed
3. Tests run automatically in CI

### **Modify Deployment**
Edit `.github/workflows/deploy.yml`:
```yaml
# Add your deployment commands
- name: Deploy to your platform
  run: |
    # Your deployment script here
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Tests Failing**
   ```bash
   # Run locally first
   make tests
   make lint
   ```

2. **Docker Build Failing**
   ```bash
   # Test locally
   make build
   docker run --rm autodeletebot:latest
   ```

3. **Quality Score Dropping**
   ```bash
   # Check pylint locally
   make lint
   # Fix issues and re-run
   ```

### **Debug Workflows**
1. Go to **Actions** tab
2. Click on failed workflow
3. Check logs for specific error
4. Use `act` for local testing (optional)

## 📚 **Useful Commands**

### **Local Development**
```bash
# Set up environment
make setup

# Run quality checks
make check

# Run tests
make tests

# Build Docker
make build

# Clean up
make clean
```

### **CI/CD Integration**
```bash
# All commands work in GitHub Actions
# No additional setup needed
```

## 🎯 **Best Practices**

### **Development Workflow**
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes & Test Locally**
   ```bash
   make tests
   make lint
   make check
   ```

3. **Push & Create PR**
   ```bash
   git push origin feature/new-feature
   # Create PR on GitHub
   ```

4. **CI/CD Runs Automatically**
   - Quality checks
   - Tests
   - Docker build
   - Security scan

5. **Merge When All Checks Pass**
   - Quality gates enforced
   - Automatic deployment to staging

### **Release Process**
1. **Create Release Tag**
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

2. **CI/CD Automatically**
   - Builds production image
   - Deploys to production
   - Creates GitHub release

## 🔗 **Integration Examples**

### **With Kubernetes**
```yaml
# Add to deploy.yml
- name: Deploy to Kubernetes
  run: |
    kubectl set image deployment/autodeletebot \
      autodeletebot=ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### **With Docker Compose**
```yaml
# Add to deploy.yml
- name: Deploy with Docker Compose
  run: |
    docker-compose -f docker-compose.prod.yml pull
    docker-compose -f docker-compose.prod.yml up -d
```

### **With Cloud Platforms**
```yaml
# Add to deploy.yml
- name: Deploy to Cloud Run
  run: |
    gcloud run deploy autodeletebot \
      --image ghcr.io/${{ github.repository }}:${{ github.sha }}
```

## 📞 **Support**

### **GitHub Issues**
- Report bugs in CI/CD workflows
- Request new features
- Ask questions about setup

### **Community**
- Check existing issues
- Review workflow examples
- Share improvements

---

**🎉 Your Auto-Delete Bot now has enterprise-grade CI/CD!**

Every push, PR, and release is automatically tested, built, and deployed with full quality assurance and security scanning.
