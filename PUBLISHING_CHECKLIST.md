# 📋 Publishing Checklist for v2.0.2

## Current Status
✅ Version is set to **2.0.2** in setup.cfg  
✅ GitHub Actions workflows created (.github/workflows/)  
⚠️ **NOT YET PUSHED** - Changes are only local  
❌ **PyPI Trusted Publisher NOT configured yet**

---

## 🚀 Step-by-Step: Publish to PyPI

### STEP 1: Configure PyPI Trusted Publisher (ONE-TIME SETUP)

**Do this BEFORE pushing to GitHub!**

1. Go to: https://pypi.org/manage/account/publishing/
2. Click **"Add a new pending publisher"**
3. Fill in the form:
   ```
   PyPI Project Name: e2D
   Owner: marick-py
   Repository name: e2D
   Workflow name: publish.yml
   Environment name: release
   ```
4. Click **"Add"**

**Why first?** This tells PyPI to trust your GitHub repository to publish packages.

---

### STEP 2: Commit and Push Your Changes

```powershell
# 1. Stage all changes
git add .

# 2. Commit
git commit -m "Add GitHub Actions CI/CD, Python 3.14 support, fix dependencies"

# 3. Push to GitHub
git push origin main
```

**What happens:** GitHub Actions will run tests, but won't publish yet (no release created).

---

### STEP 3: Create a GitHub Release

#### Option A: Via GitHub Website (Easier)

1. Go to: https://github.com/marick-py/e2D/releases/new
2. Fill in:
   - **Tag**: `v2.0.2` (MUST start with 'v' and match version in setup.cfg)
   - **Release title**: `v2.0.2` or `Version 2.0.2 - ModernGL Rewrite`
   - **Description**: Copy content from `docs/RELEASE_NOTES_v2.0.2.md`
3. Click **"Publish release"**

#### Option B: Via Command Line

```powershell
# Create and push a tag
git tag v2.0.2
git push origin v2.0.2

# Then go to GitHub and convert the tag to a release
```

---

### STEP 4: Watch the Magic Happen! ✨

1. Go to: https://github.com/marick-py/e2D/actions
2. You'll see the "Publish to PyPI" workflow running
3. Wait ~2-5 minutes
4. Check: https://pypi.org/project/e2D/

**The workflow automatically:**
- ✅ Checks out your code
- ✅ Sets up Python 3.13
- ✅ Installs build tools
- ✅ Compiles Cython extensions
- ✅ Builds wheel and source distributions
- ✅ Publishes to PyPI (using Trusted Publisher, no tokens!)

---

## 🎯 Quick Summary

```
Current State → Action → Result
─────────────────────────────────────────────────────────
Local changes  → Push to GitHub     → Tests run automatically
Tag v2.0.2     → Create Release     → Publishes to PyPI automatically
```

---

## ⚠️ Important Notes

### Version Number Must Match!
- `setup.cfg`: version = **2.0.2**
- `e2D/__init__.py`: __version__ = **"2.0.2"**
- GitHub tag: **v2.0.2** (with 'v' prefix)

### If Publishing Fails:
1. Check: https://github.com/marick-py/e2D/actions for error messages
2. Common issues:
   - PyPI Trusted Publisher not configured → Configure it first!
   - Project name mismatch → Must be exactly "e2D"
   - Version already exists on PyPI → Bump version number

### After First Successful Publish:
All future releases are just:
1. Update version with `python new_version.py`
2. Commit and push
3. Create GitHub release
4. Done! 🎉

---

## 🔄 Next Release (Example: v2.0.3)

```powershell
# 1. Update version
python new_version.py
# Type: 2.0.3

# 2. Commit and push
git add .
git commit -m "Bump version to 2.0.3"
git push

# 3. Create release on GitHub with tag v2.0.3
# 4. GitHub Actions publishes automatically!
```

No more batch files, no more manual uploads! 🚀
