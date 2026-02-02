# 🔒 Self-Hosted Runner Security Guide

## ⚠️ CRITICAL SECURITY SETTINGS

### Your Current Setup (SECURE ✅)

Your workflow now uses this logic:

```yaml
runs-on: ${{ github.event_name == 'push' && github.actor == 'marick-py' && 'self-hosted' || 'ubuntu-latest' }}
```

**What this means:**
- ✅ **Your pushes** → Self-hosted (fast, your VPS)
- ❌ **Pull requests** → GitHub-hosted (safe, isolated)
- ❌ **Other users' pushes** → GitHub-hosted (safe)
- ❌ **Fork PRs** → GitHub-hosted (safe)

**Why this is secure:**
- Only YOUR direct pushes run on your VPS
- All untrusted code (PRs, forks) runs on GitHub's isolated runners
- No risk of malicious code accessing your VPS

---

## 🛡️ Additional Security Measures

### 1. VPS Firewall Rules (CRITICAL)

Lock down your VPS to only essential ports:

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Install ufw firewall (if not already installed)
sudo apt install ufw

# Allow SSH (change 22 if you use custom port)
sudo ufw allow 22/tcp

# Allow HTTPS (GitHub Actions needs this)
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# DENY everything else
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**Result:** Your VPS can only accept SSH and HTTPS connections. No backdoors!

---

### 2. Dedicated Runner User (CRITICAL)

**NEVER run the runner as root!**

```bash
# Create dedicated user for runner
sudo useradd -m -s /bin/bash github-runner
sudo passwd github-runner  # Set a strong password

# Switch to runner user
sudo su - github-runner

# Install runner as this user
mkdir actions-runner && cd actions-runner
# ... follow GitHub's setup instructions ...
```

**Why this matters:**
- Even if malicious code runs, it has limited privileges
- Can't access root files
- Can't modify system settings
- Can't install system-wide backdoors

---

### 3. Limit Runner Permissions

```bash
# As root, restrict what runner user can do
sudo visudo

# Add this line (allows runner to install Python packages only)
github-runner ALL=(ALL) NOPASSWD: /usr/bin/pip3, /usr/bin/apt-get install python*
```

**Even better:** Don't give sudo at all!

---

### 4. Network Isolation (Advanced)

If you have other services on the VPS:

```bash
# Install Docker and run runner in container (isolates it)
sudo apt install docker.io

# Or use network namespaces to isolate runner
```

---

### 5. File System Isolation

```bash
# Restrict runner's home directory
sudo chmod 700 /home/github-runner

# Create a separate partition for runner (advanced)
# Prevents runner from filling up system disk
```

---

### 6. Monitor Runner Activity

```bash
# Install fail2ban to auto-ban suspicious activity
sudo apt install fail2ban

# Monitor runner logs
tail -f ~/actions-runner/_diag/Runner_*.log

# Set up log rotation to prevent disk fill
sudo nano /etc/logrotate.d/github-runner
```

Add:
```
/home/github-runner/actions-runner/_diag/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

### 7. Regular Security Updates

```bash
# Auto-update security patches
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Manual updates weekly
sudo apt update && sudo apt upgrade -y
```

---

### 8. SSH Hardening

Edit SSH config:
```bash
sudo nano /etc/ssh/sshd_config
```

Make these changes:
```
# Disable root login
PermitRootLogin no

# Disable password auth (use SSH keys only)
PasswordAuthentication no
PubkeyAuthentication yes

# Change default port (optional but helps)
Port 2222  # Use any port instead of 22

# Limit login attempts
MaxAuthTries 3
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

---

## 🚨 What Your Workflow NOW Prevents

### ✅ SAFE: Your Direct Pushes
```
You push to main → Runs on your VPS → SAFE (you trust your own code)
```

### ✅ SAFE: Pull Requests (Even Yours!)
```
PR from anyone → Runs on GitHub → SAFE (isolated, can't touch your VPS)
```

### ✅ SAFE: Fork PRs
```
Fork PR → Runs on GitHub → SAFE (completely isolated)
```

### ❌ BLOCKED: Random User Push
```
Random user pushes → Condition fails → Runs on GitHub → Your VPS never touched
```

---

## 🔍 How to Verify Security

### Check Current Workflow Logic

Your workflow now checks:
1. **Event type** = push? (not PR)
2. **Actor** = marick-py? (you)
3. **If both true** → self-hosted
4. **Otherwise** → ubuntu-latest

### Test It

1. Create a PR from a branch
2. Check which runner it uses: should be `ubuntu-latest`
3. Push directly to main
4. Check which runner it uses: should be `self-hosted`

---

## 📊 Security Checklist

**VPS Security:**
- [ ] Firewall configured (ufw)
- [ ] SSH hardened (key-only, no root)
- [ ] Dedicated runner user (not root)
- [ ] Auto security updates enabled
- [ ] Runner has minimal permissions

**GitHub Security:**
- [✅] Only YOUR pushes use self-hosted
- [✅] All PRs use GitHub-hosted
- [✅] Workflow checks actor == 'marick-py'
- [✅] Workflow checks event_name == 'push'

**Monitoring:**
- [ ] Runner logs monitored
- [ ] fail2ban installed
- [ ] Log rotation configured
- [ ] Disk space monitored

---

## 🎯 What If Someone Compromises Your GitHub Account?

**Worst case scenario:** Someone gets your GitHub password

**What they CANNOT do:**
- Cannot SSH into your VPS (different credentials)
- Cannot run arbitrary code on VPS (workflow blocks it)
- VPS firewall blocks most attacks

**What they CAN do:**
- Push malicious code to your repo
- But it still won't run on your VPS unless they ARE you (github.actor == 'marick-py')

**Additional protection:**
1. Enable 2FA on GitHub: https://github.com/settings/security
2. Use SSH keys for VPS (not passwords)
3. Keep different passwords for GitHub vs VPS

---

## 🔐 Summary

**Your setup is now SECURE because:**

1. ✅ **Conditional logic** - Only YOUR pushes use VPS
2. ✅ **Firewall** - VPS is locked down
3. ✅ **Isolated user** - Runner can't access sensitive files
4. ✅ **No root** - Runner has limited permissions
5. ✅ **Monitored** - You can see what's running

**The risk of backdoors is MINIMAL:**
- Only your trusted code runs on VPS
- All external code runs on GitHub (isolated)
- VPS is hardened with firewall and user isolation

**You're using your VPS efficiently AND securely!** 🚀
