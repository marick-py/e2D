import configparser as cp
cfg = cp.ConfigParser()
_ = cfg.read("setup.cfg")
current_version = cfg.get("metadata", "version")
new_version = input(f"Current version: [{current_version}]\n>>> ")
if new_version != "":
    cfg.set("metadata", "version", new_version)
with open("setup.cfg", "w") as config_file:
    cfg.write(config_file)