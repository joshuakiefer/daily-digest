# Testing the Installation Script

How to test `install.sh` locally before deploying.

## 🧪 Local Testing

### Test on your local machine:

```bash
cd ~/daily-digest

# Test the script
bash install.sh
```

### Test in a clean environment:

**Using Docker** (recommended):
```bash
# Test on Ubuntu 22.04
docker run -it ubuntu:22.04 bash

# Inside container:
apt update && apt install -y curl
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
```

**Using Vagrant** (if you have it):
```bash
# Create Vagrantfile
cat > Vagrantfile << 'EOF'
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
end
EOF

vagrant up
vagrant ssh

# Inside VM:
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
```

## 🔍 Testing Checklist

Run through each step:

- [ ] Script downloads correctly
- [ ] OS detection works
- [ ] Dependencies install without errors
- [ ] Python environment creates successfully
- [ ] All packages install
- [ ] Interactive prompts work correctly
- [ ] .env file created with correct format
- [ ] Systemd service creates (if accepted)
- [ ] Application starts
- [ ] Health check endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs accessible: `curl http://localhost:8000/docs`

## 🐛 Common Issues During Testing

### "Permission denied" for pip installs:
```bash
# Make sure you're in virtual environment
which python  # Should show path to venv/bin/python
```

### Systemd commands fail:
```bash
# Normal if not running on systemd-based system
# Skip systemd setup during testing
```

### Port already in use:
```bash
# Kill existing process
pkill -f uvicorn
# Or change port in script
```

## ✅ Pre-Deployment Checklist

Before sharing your install script:

- [ ] Update `GITHUB_REPO` variable in install.sh
- [ ] Push all code to GitHub
- [ ] Make repository public (or handle authentication)
- [ ] Test the actual curl command:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
  ```
- [ ] Test on fresh Ubuntu 20.04 droplet
- [ ] Test on fresh Ubuntu 22.04 droplet
- [ ] Verify all prompts are clear
- [ ] Check error messages are helpful
- [ ] Ensure script is idempotent (safe to run multiple times)

## 🚀 Deploying the Installer

### 1. Push to GitHub:
```bash
cd ~/daily-digest
git init
git add .
git commit -m "Add one-line installer"
git branch -M main
git remote add origin https://github.com/joshuakiefer/daily-digest.git
git push -u origin main
```

### 2. Update documentation:
- Replace `YOUR_USERNAME` in install.sh
- Update README.md with correct URL
- Update INSTALL.md with correct URL

### 3. Create a release (optional but recommended):
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

### 4. Test from actual URL:
```bash
# On a fresh droplet
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
```

## 📝 Tips for a Great Installer

### Make it safe:
```bash
set -e  # Exit on any error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failures
```

### Give clear feedback:
- Use colors for different message types
- Show progress for long operations
- Explain what's happening at each step

### Handle errors gracefully:
```bash
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Installing..."
    # Install it
fi
```

### Ask permission for destructive operations:
```bash
if [ -d "$APP_DIR" ]; then
    if ask_yes_no "Directory exists. Overwrite?" "n"; then
        rm -rf "$APP_DIR"
    fi
fi
```

### Provide helpful output at the end:
- Show what was installed
- List next steps
- Show how to check logs
- Provide troubleshooting links

## 🔄 Updating After Changes

When you update your app:

```bash
git add .
git commit -m "Update application"
git push

# Users can reinstall with:
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash
# Answer "yes" to overwrite existing installation
```

## 📚 Resources

- [Bash best practices](https://bertvv.github.io/cheat-sheets/Bash.html)
- [Shell script security](https://www.shellcheck.net/)
- [Advanced bash scripting guide](https://tldp.org/LDP/abs/html/)

## 🎯 Example Test Session

```bash
# Fresh Ubuntu droplet
ssh root@your-droplet

# Run installer
curl -fsSL https://raw.githubusercontent.com/joshuakiefer/daily-digest/main/install.sh | bash

# Follow prompts...
# After completion:

# Test health
curl http://localhost:8000/health

# Test digest
curl -X POST http://localhost:8000/digest/quick

# Check service
systemctl status daily-digest

# View logs
journalctl -u daily-digest --no-pager -n 50

# Success! ✅
```
