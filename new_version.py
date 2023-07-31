import configparser as cp
import os

cfg = cp.ConfigParser()
_ = cfg.read("setup.cfg")
current_version = cfg.get("metadata", "version")
new_version = input(f"Current version: [{current_version}]\n>>> ")
cfg.set("metadata", "version", new_version)
with open("setup.cfg", "w") as config_file:
    cfg.write(config_file)

os.system("python -m build")
os.system("python -m twine upload -u marick-py --skip-existing --repository pypi dist/*")