"""
Version updater for e2D package
Updates version in both setup.cfg and __init__.py
"""

import configparser as cp
import re

# Read current version from setup.cfg
cfg = cp.ConfigParser()
_ = cfg.read("setup.cfg")
current_version = cfg.get("metadata", "version")

print(f"e2D Package Version Updater")
print(f"=" * 50)
print(f"Current version: {current_version}")
print(f"=" * 50)

new_version = input("Enter new version (or press Enter to keep current): ").strip()

if new_version and new_version != current_version:
    # Update setup.cfg
    cfg.set("metadata", "version", new_version)
    with open("setup.cfg", "w") as config_file:
        cfg.write(config_file)
    print(f"✓ Updated setup.cfg to version {new_version}")
    
    # Update e2D/__init__.py
    try:
        with open("e2D/__init__.py", "r", encoding="utf-8") as f:
            init_content = f.read()
        
        # Replace version string
        updated_content = re.sub(
            r'__version__\s*=\s*["\'][\d.]+["\']',
            f'__version__ = "{new_version}"',
            init_content
        )
        
        with open("e2D/__init__.py", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"✓ Updated e2D/__init__.py to version {new_version}")
    except Exception as e:
        print(f"⚠ Warning: Could not update __init__.py: {e}")
    
    # Update e2D/__init__.py
    try:
        with open("e2D/__init__.py", "r", encoding="utf-8") as f:
            init_content = f.read()
        
        # Replace version string
        updated_content = re.sub(
            r'__version__\s*=\s*["\'][\d.]+["\']',
            f'__version__ = "{new_version}"',
            init_content
        )
        
        with open("e2D/__init__.py", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"✓ Updated e2D/__init__.py to version {new_version}")
    except Exception as e:
        print(f"⚠ Warning: Could not update __init__.py: {e}")
    
    # Update README.md version history
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
        
        # Replace current version in 2.x history
        updated_readme = re.sub(
            r'- \*\*\d+\.\d+\.\d+\*\* \(Current\)',
            f'- **{new_version}** (Current)',
            readme_content
        )
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated_readme)
        
        print(f"✓ Updated README.md version history to {new_version}")
    except Exception as e:
        print(f"⚠ Warning: Could not update README.md: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Version updated successfully to {new_version}")
    print(f"{'=' * 50}")
else:
    print("\nNo changes made.")
